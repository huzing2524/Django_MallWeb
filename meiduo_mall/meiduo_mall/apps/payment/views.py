import os
from alipay import AliPay
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import OrderInfo
from payment.models import Payment


# GET /orders/(?P<order_id>\d+)/payment/
class PaymentView(APIView):
    """支付宝订单支付
    获取支付链接(向阿里服务器发送请求，返回给用户阿里支付界面链接)"""

    def get(self, request, order_id):
        user = request.user
        try:
            order = OrderInfo.objects.get(
                order_id=order_id,
                user=user,
                status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"],
                pay_method=OrderInfo.PAY_METHODS_ENUM["ALIPAY"]
            )
        except OrderInfo.DoesNotExist:
            return Response({"message": "订单信息有误"}, status=status.HTTP_400_BAD_REQUEST)

        # 向支付宝发送请求，获取支付链接参数
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 阿里服务器post提交程序服务器告知支付信息
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            # 支付宝的公钥，验证支付宝回传消息使用，不是自己的公钥
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",  # RSA or RSA2
            # True为沙箱环境
            debug=settings.ALIPAY_DEBUG  # False by default
        )

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay_client.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单编号
            total_amount=str(order.total_amount),  # 总金额
            subject="美多商城订单%s" % order_id,  # 订单标题
            return_url="http://www.meiduo.site:8080/pay_success.html",  # 支付完成后回调网址
            notify_url=None  # 可选, 不填则使用默认notify url
        )

        # 拼接支付链接网址
        alipay_url = settings.ALIPAY_URL + "?" + order_string

        return Response({"alipay_url": alipay_url})


# charset=utf-8
# &out_trade_no=20180704082900000000001
# &method=alipay.trade.page.pay.return
# &total_amount=3788.00
# &trade_no=2018070421001004630200569950
# &auth_app_id=2016081600258081
# &version=1.0&app_id=2016081600258081&sign_type=RSA2&seller_id=2088102171419163&timestamp=2018-07-04+16%3A31%3A49
# &sign=UNn3nCckqp4E3MJAonwiywZBtP5Wiia6eJVUta0iimZeLdUuMhH%2FdyRmPGgaQ6xHn0u5KCQbeof4dsXyh%2FdG42cLho9LYCcRqwa6qv3BbEx1J3Y9Qxp6ye%2BTmQq9UbW3%2FoXdAjVJ0gChPQNjm%2BCMI0XbLPT9ARyclb3oKMHrNB7kixMma8OIQbztylSbIwnQilQlxhIWzDqhxCXRgAXjRir7748YpkzW%2FlpkTyuxU1mKI4VwvxV8Of4PQqZcLU%2BbXo2SI%2Bm0Vy%2FgMae4hZIRf%2BbTI1C8lw203HpOMDDeZiUea3GpF9WzuZkTPc4Ryv%2F8K3F6e2IvInpeQt48nqNC%2BQ%3D%3D

# PUT /payment/status/?支付宝参数
class PaymentStatusView(APIView):
    """保存支付结果
    用户支付成功后，支付宝会将用户重定向到http://www.meiduo.site:8080/pay_success.html，并携带支付结果数据"""

    def put(self, request):
        alipay_req_data = request.query_params  # QueryDict
        if not alipay_req_data:
            return Response({"message": "缺少参数"}, status=status.HTTP_400_BAD_REQUEST)

        alipay_req_dict = alipay_req_data.dict()
        sign = alipay_req_dict.pop("sign")

        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 阿里服务器post提交程序服务器告知支付信息
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            # 支付宝的公钥，验证支付宝回传消息使用，不是自己的公钥
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",  # RSA or RSA2
            # True为沙箱环境
            debug=settings.ALIPAY_DEBUG  # False by default
        )

        # verify()使用支付宝公钥解密验证url查询字符串内容是否被篡改，加密过程为：支付宝服务器把参数内容经过哈希摘要算法生成固定长度内容然后使用支付宝私钥加密
        # 返回验证结果: True/False
        result = alipay_client.verify(alipay_req_dict, sign)

        if result:
            order_id = alipay_req_dict.get("out_trade_no")
            trade_id = alipay_req_dict.get("trade_no")
            # 保存美多商城订单编号和支付宝交易流水号
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 修改订单交易状态
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM["UNSEND"])
            return Response({"trade_id": trade_id})
        else:
            return Response({"message": "参数错误"}, status=status.HTTP_400_BAD_REQUEST)
