from django.shortcuts import render
import itsdangerous
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.exceptions import OAuthQQAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import OAuthQQ


class QQAuthURLView(APIView):
    """step1: 获取QQ登录的url"""
    def get(self, request):
        """GET /oauth/qq/authorization/?next=/user_center_info.html"""
        next = request.query_params.get("next")
        # 拼接QQ登录的url
        oauth_qq = OAuthQQ(state=next)
        login_url = oauth_qq.get_login_url()

        return Response({"login_url": login_url})


class QQAuthUserView(CreateAPIView):
    """
    step4: 获取qq登录的用户数据
    """
    # 用户是第一次用QQ登录，使用post提交表单，使用序列化器校验参数、创建用户模型
    serializer_class = OAuthQQUserSerializer

    def get(self, request):
        """
        GET /oauth/qq/user/?code=xxx
        :param request:
        :return:
        1. 如果用户是第一次使用QQ登录，返回access_token(包含openid)
        2. 如果用户不是第一次使用QQ登录，返回JWT token, username, user_id
        """
        code = request.query_params.get("code")

        if not code:
            return Response({"message": "缺少code"}, status=status.HTTP_400_BAD_REQUEST)

        oauth_qq = OAuthQQ()

        try:
            # 通过授权的code获取access_token(开发者身份标识)
            access_token = oauth_qq.get_access_token(code)
            # 通过access_token获取openid(用户唯一身份标识)
            openid = oauth_qq.get_openid(access_token)
        except OAuthQQAPIError:
            return Response({'message': '访问QQ接口异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 根据openid查询数据库OAuthQQUser，判断用户是否存在
        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 用户不存在，说明之前没有注册过，把openid加密成JWT然后直接返回，要求用户填写资料注册账号
            access_token = oauth_qq.generate_bind_user_access_token(openid)
            return Response({"access_token": access_token})
        else:
            # 用户存在，表示QQ已经绑定过本网站账号，直接签发JWT返回
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            user = oauth_qq_user.user  # 用户模型对象取出user字段信息
            payload = jwt_payload_handler(user)  # 放入载荷中
            token = jwt_encode_handler(payload)  # 生成JWT Token

            response = Response({
                "username": user.username,
                "user_id": user.id,
                "token": token
            })

            # TODO response = merge_cart_cookie_to_redis(request, user, response)

            return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        return response
