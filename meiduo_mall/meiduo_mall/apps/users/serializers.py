# -*- coding: utf-8 -*-
import re
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """创建用户账户序列化器"""
    # post 提交时额外需要校验的字段，数据库中User中没有
    # write_only=True 该字段只在反序列化验证时生效
    password2 = serializers.CharField(label="确认密码", write_only=True)
    sms_code = serializers.CharField(label="短信验证码", write_only=True)
    allow = serializers.CharField(label="同意协议", write_only=True)
    # 只在序列化向前端响应的时候，才生成token，发送给前端
    token = serializers.CharField(label="JWT token", read_only=True)

    class Meta:
        model = User
        # 指定所有的字段，包括数据库模型类字段和自定义添加的字段
        fields = ("id", "username", "password", "password2", "sms_code", "mobile", "allow", "token")
        extra_kwargs = {
            "username": {
                "min_length": 5,
                "max_length": 20,
                "error_messages": {
                    "min_length": "仅允许5-20个字符的用户名",
                    "max_length": "仅允许5-20个字符的用户名"
                }
            },
            "password": {
                "write_only": True,
                "min_length": 8,
                "max_length": 20,
                "error_messages": {
                    "min_length": "仅允许8-20个字符的密码",
                    "max_length": "仅允许8-20个字符的密码"
                }
            }
        }

    def validate_mobile(self, value):
        """校验手机号"""
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("手机号格式错误")

        return value

    def validate_allow(self, value):
        """校验是否同意用户协议"""
        if value != "true":
            raise serializers.ValidationError("请同意用户协议")

        return value

    def validate(self, data):
        """校验多个字段"""
        # 对比两次输入的密码是否一致
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("两次密码不一致")

        # 校验短信验证码
        redis_conn = get_redis_connection("verify_codes")
        mobile = data["mobile"]
        real_sms_code = redis_conn.get("sms_%s" % mobile)

        if real_sms_code is None:
            raise serializers.ValidationError("短信验证码已失效")

        if data["sms_code"] != real_sms_code.decode():
            raise serializers.ValidationError("短信验证码错误")

        return data

    def create(self, validated_data):
        """
        保存用户账号
        :param validated_data: 字典
        :return: 用户模型类
        """
        # 移除只在校验时需要，数据库模型中不存在的字段
        del validated_data["password2"]
        del validated_data["sms_code"]
        del validated_data["allow"]

        # 可以使用django原生的管理器创建模型对象然后保存，需要解包
        # user = User.objects.create(**validated_data)

        # 也可以调用父类ModelSerializer的create()方法，已进行解包
        user = super().create(validated_data)

        # 加密 密码
        user.set_password(validated_data["password"])
        user.save()

        # 签发jwt token
        # "token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6IjMyXHU3OGM1XHU5MWNkXHU3Njg0XHU2Y2U1XHU5Y2M1IiwiZXhwIjoxNTMzOTA2NjQyLCJlbWFpbCI6IiJ9.NMSTwvnzmmYKRCHuwI21LIwAGciJNPmTK1Pkb_FeoO0"
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 生成载荷和签名
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # 把token保存到用户模型中
        user.token = token

        return user
