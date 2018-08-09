import logging
import random
from django.http import HttpResponse
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_mall.libs.captcha.captcha import captcha
from verifications import constants
from verifications.serializers import ImageCodeCheckSerializer
from celery_tasks.sms.tasks import send_sms_code

logger = logging.getLogger("django")

# Create your views here.


# GET /image_codes/(?P<image_code_id>[\w-]+)/
class ImageCodeView(APIView):
    """图片验证码"""

    def get(self, request, image_code_id):
        # 生成4位图片验证码的文本，验证码图片
        text, image = captcha.generate_captcha()

        logger.info("[图片验证码是: %s]" % text)

        # 生成一个redis连接对象
        redis_conn = get_redis_connection("verify_codes")
        # 保存到redis数据库中
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # 使用HttpResponse返回图片，不能使用Response
        return HttpResponse(image, content_type="image/jpg")


#  GET /sms_codes/(?P<mobile>1[3-9]\d{9})/?image_code_id=xxx&text=xxx
class SMSCodeView(GenericAPIView):
    """短信验证码"""
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 让序列化器校验参数
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)

        logger.info("[短信验证码是: %s]" % sms_code)

        redis_conn = get_redis_connection("verify_codes")
        # 使用redis的管道收集多条命令，然后一起执行，减少网络IO耗时操作
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存短信验证码的发送标志
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 使用celery发送短信验证码
        expires = constants.SMS_CODE_REDIS_EXPIRES // 60  # "//" 除法结果为整数
        send_sms_code.delay(mobile, sms_code, expires, constants.SMS_CODE_TEMP_ID)

        return Response({"message": "OK"})
