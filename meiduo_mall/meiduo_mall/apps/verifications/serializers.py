# -*- coding: utf-8 -*-
from rest_framework import serializers, status
from django_redis import get_redis_connection


class ImageCodeCheckSerializer(serializers.Serializer):
    """图片验证码校验序列化器/限制短信验证码发送频次"""
    # 图片验证码的uuid编号
    image_code_id = serializers.UUIDField()
    # 用户输入的图片验证码文本内容
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        image_code_id = attrs["image_code_id"]
        text = attrs["text"]

        redis_conn = get_redis_connection("verify_codes")
        real_image_code_text = redis_conn.get("img_%s" % image_code_id)

        if not real_image_code_text:
            raise serializers.ValidationError("图片验证码已过期")

        # 删除图片验证码，只让它在当前验证环节生效。防止这个图片验证码多次请求短信验证码
        redis_conn.delete("img_%s" % image_code_id)

        # redis中保存的数据字节类型，需要先解码
        real_image_code_text = real_image_code_text.decode()
        if real_image_code_text.lower() != text.lower():
            raise serializers.ValidationError("图片验证码失败")

        # get_serializer()方法在创建序列化器对象的时候，会补充context属性
        # 包含request, format, view类视图对象
        # django的类视图对象中，kwargs中保存了url路径中提取出来的查询字符串参数
        mobile = self.context["view"].kwargs["mobile"]

        # 限制短信验证码的发送次数
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            raise serializers.ValidationError("请求次数过于频繁")

        return attrs






