from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView

from users import serializers
from users.models import User


# POST /users/
class UserView(CreateAPIView):
    """创建用户账号"""
    serializer_class = serializers.CreateUserSerializer


# GET usernames/(?P<username>\w{5,20})/count/
class UsernameCountView(APIView):
    """用户注册界面：姓名是否重名的校验"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            "username": username,
            "count": count
        }

        return Response(data)


# GET mobiles/(?P<mobile>1[3-9]\d{9})/count
class MobileCountView(APIView):
    """用户注册界面：手机号是否重复校验"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "mobile": mobile,
            "count": count
        }

        return Response(data)


# GET /user/
class UserDetailView(RetrieveAPIView):
    """个人中心：显示用户信息"""
    serializer_class = serializers.UserDetailSerializer
    # 父类APIView中可以在某个视图类中设置认证权限
    permission_classes = [IsAuthenticated]  # 仅通过认证的用户才能访问该视图获取用户信息

    def get_object(self):
        """
        请求的url路径中没有用户的id，需要重写get_object()方法查询出当前的用户对象
        :return: 返回当前请求的用户
        """
        # django的View父类中的as_view()方法添加了self.request = request
        # request.user 当前请求的用户对象
        return self.request.user


# PUT /email/
class EmailVIew(UpdateAPIView):
    """个人中心：修改邮箱地址"""
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # 用户模型中有所有字段(包括邮箱地址)


# GET /emails/verification/?token=xxx
class VerifyEmailView(APIView):
    """个人中心：邮箱链接校验"""

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"message": "缺少token"}, status=status.HTTP_400_BAD_REQUEST)

        # 校验token，返回用户模型对象
        user = User.check_verify_email_token(token)
        if not user:
            return Response({"message": "链接失效"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 用户邮箱通过验证，设置为已激活状态
            user.email_active = True
            user.save()

        return Response({"message": "邮箱验证成功"})


