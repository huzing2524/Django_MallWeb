# -*- coding: utf-8 -*-
import re
from django.contrib.auth.backends import ModelBackend
from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """自定义JWT(Json web token)认证"""
    return {
        "token": token,
        "user_id": user.id,
        "username": user.username
    }


def get_user_by_account(account):
    """
    根据传入的不同类型账号查询用户
    :param account: 用户输入账号，手机号或用户名
    :return: 用户模型对象
    """
    try:
        if re.match(r"1[3-9]\d{9}$", account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义的用户认证类"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 重写父类用户认证方法
        user = get_user_by_account(username)

        if user is not None and user.check_password(password):
            return user
