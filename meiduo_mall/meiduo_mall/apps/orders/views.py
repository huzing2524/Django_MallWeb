from _decimal import Decimal
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from goods.models import SKU
from orders.serializers import OrderSettlementSerializer, SaveOrderSerializer

"""
{
    "freight":"10.00",
    "skus":[
        {
            "id":10,
            "name":"华为 HUAWEI P10 Plus 6GB+128GB 钻雕金 移动联通电信4G手机 双卡双待",
            "default_image_url":"http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRchWAMc8rAARfIK95am88158618",
            "price":"3788.00",
            "count":1
        },
        ......
}
"""


class OrderSettlementView(GenericAPIView):
    """从购物车中选中的商品生成订单"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        redis_conn = get_redis_connection("cart")

        # redis_cart = {
        #     商品的sku_id(bytes类型): count数量(bytes类型)
        #     1: 1
        #     16: 2
        #    ...
        # }
        redis_cart_dict = redis_conn.hgetall("cart_%s" % request.user.id)  # 购物车中所有商品的sku_id，字典
        # set(勾选的商品sku_id(bytes类型), 1, 3, 16,....)
        redis_cart_selected = redis_conn.smembers("cart_selected_%s" % request.user.id)  # 购物车中被选中商品的sku_id，集合

        cart = {}  # {sku_id: count}
        for sku_id in redis_cart_selected:
            # 把某个商品的数量和cart字典的id组成键值对
            cart[int(sku_id)] = int(redis_cart_dict[sku_id])

        redis_id_list = cart.keys()
        sku_obj_list = SKU.objects.filter(id__in=redis_id_list)

        for sku in sku_obj_list:
            sku.count = cart[sku.id]  # 把商品的数量添加到sku的属性上

        freight = Decimal("10.00")  # 运费
        serializer = OrderSettlementSerializer({"freight": freight, "skus": sku_obj_list})

        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    """保存订单"""
    serializer_class = SaveOrderSerializer
    permission_classes = [IsAuthenticated]
