from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from users.models import User
from users.serializers import CreateUserSerializer

# Create your views here.


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


# POST /users/
class UserView(CreateAPIView):
    """创建用户账号"""
    serializer_class = CreateUserSerializer


