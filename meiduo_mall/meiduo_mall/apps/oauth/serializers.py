# -*- coding: utf-8 -*-
import logging
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser
from oauth.utils import OAuthQQ
from users.models import User
logger = logging.getLogger("django")


class OAuthQQUserSerializer(serializers.ModelSerializer):
    """第三方QQ登录 序列化器"""
    # 下面是数据库模型类User上没有的字段，需要额外补充并校验
    sms_code = serializers.CharField(label="短信验证码", write_only=True)  # 只在反序列化接收的时候需要校验
    access_token = serializers.CharField(label="操作凭证", write_only=True)  # 反序列化接收时校验access_token(加密后的openid)是否被篡改
    token = serializers.CharField(label="登录成功凭证", read_only=True)  # 只在序列化时返回登录成功的JWT token
    mobile = serializers.RegexField(label="手机号码", regex=r"^1[3-9]\d{9}$")  # 正则表达式匹配字段

    class Meta:
        model = User
        # 要包含所有的字段，包括数据库的模型类字段和自定义需要校验的其它字段
        fields = ("mobile", "password", "sms_code", "access_token", "id", "username", "token")
        extra_kwargs = {
            "username": {
                "read_only": True  # 数据库User模型类上已有的字段，只需要在序列化时返回
            },
            "password": {
                "write_only": True,  # 数据库User模型类上已有的字段，只需要在反序列化时校验
                "min_length": 8,
                "max_length": 20,
                "error_messages": {
                    "min_length": "仅允许8-20个字符的密码",
                    "max_length": "仅允许8-20个字符的密码"
                }
            }
        }

    def validate(self, attrs):
        """校验access_token和短信验证码"""
        access_token = attrs["access_token"]
        # 校验access_token是否被篡改，取出用户在QQ上的openid
        openid = OAuthQQ.check_bind_user_access_token(access_token)
        if not openid:
            raise serializers.ValidationError("无效的access_token")
        attrs["openid"] = openid  # 保存到attrs中，验证通过后传递给validated_data

        # 校验短信验证码
        mobile = attrs["mobile"]
        sms_code = attrs["sms_code"]
        redis_conn = get_redis_connection("verify_codes")
        real_sms_code = redis_conn.get("sms_%s" % mobile)
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError("短信验证码错误")

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist as e:
            logger.error("用户不存在：%s" % e)
        else:
            # 如果用户存在，校验密码
            password = attrs["password"]
            # 把用户输入的原始明文密码与数据库保存的加密后密码进行对比
            if not user.check_password(password):
                raise serializers.ValidationError("密码错误")
            # 密码一致，把用户模型保存到attrs中记录，以便在validated_data可以取出
            attrs["user"] = user

        return attrs

    def create(self, validated_data):
        """
        创建用户模型
        :param validated_data: 验证完成后的数据
        :return: 返回创建后的用户模型
        """
        openid = validated_data["openid"]
        # user可能存在也可能不存在，所以只能用get尝试获取，不能以键取值(报错 KeyError: 'user')
        user = validated_data.get("user")  # 用户不存在返回None
        mobile = validated_data["mobile"]
        password = validated_data["password"]

        if not user:
            # 如果用户不存在，先创建用户，然后绑定openid（创建OAuthQQUser数据）
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        # 如果用户已经存在，可以直接在OAuthQQUser中创建模型，绑定与User中的外键
        OAuthQQUser.objects.create(user=user, openid=openid)

        # 签发JWT token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token  # 把token保存到用户模型中

        self.context["view"].user = user

        return user


