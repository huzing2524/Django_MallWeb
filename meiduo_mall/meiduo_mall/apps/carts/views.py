import base64
import pickle
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from carts import constants
from carts.serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer, CartSelectAllSerializer
from goods.models import SKU


class CartView(GenericAPIView):
    """购物车"""
    serializer_class = CartSerializer

    def perform_authentication(self, request):
        """重写父类权限校验，让未登录用户进入视图"""
        pass

    def post(self, request):
        """添加保存商品到购物车"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.validated_data["sku_id"]
        count = serializer.validated_data["count"]
        selected = serializer.validated_data["selected"]

        try:
            # 登录用户返回正常用户user，未登录用户返回匿名用户AnonymoseUser
            user = request.user
        except Exception:
            user = None

        # 用户已登录 and 用户已授权(JWT Token校验通过)，商品保存到redis中
        # 必须通过is_authenticated检查，才能表明是已登录通过验证的用户；user有值可能为未登录的匿名用户
        if user and user.is_authenticated:
            redis_conn = get_redis_connection("cart")
            pl = redis_conn.pipeline()
            # 记录购物车商品数量
            pl.hincrby("cart_%s" % user.id, sku_id, count)  # hash类型

            if selected:
                # 商品勾选状态
                pl.sadd("cart_selected_%s" % user.id, sku_id)  # set类型

            pl.execute()
            return Response(serializer.data)
        # 用户未登录时，商品数据保存到cookie中
        else:
            cart_str = request.COOKIES.get("cart")

            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                # 商品在购物车中
                cart_dict[sku_id]["count"] += count
                cart_dict[sku_id]["selected"] = selected
            else:
                # 商品不在购物车中
                cart_dict[sku_id] = {
                    "count": count,
                    "selected": selected
                }

            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response = Response(serializer.data)
            response.set_cookie("cart", cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)

            return response

    def get(self, request):
        """查询购物车商品"""
        try:
            user = request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            # 已登录用户从redis中查询购物车商品
            redis_conn = get_redis_connection("cart")
            # redis_cart = {
            #     商品的sku_id(bytes类型): count数量(bytes类型)
            #     1: 1
            #     16: 2
            #    ...
            # }
            redis_cart = redis_conn.hgetall("cart_%s" % user.id)
            # set(勾选的商品sku_id(bytes类型), 1, 3, 16,....)
            redis_cart_selected = redis_conn.smembers("cart_selected_%s" % user.id)

            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    "count": int(count),
                    "selected": sku_id in redis_cart_selected
                }
        else:
            # 未登录匿名用户从cookie中查询购物车商品
            cookie_cart = request.COOKIES.get("cart")
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}

            # cart_dict = {
            #     sku_id_1: {
            #         'count': 10
            #         'selected': True
            #     },
            #     sku_id_2: {
            #         'count': 10
            #         'selected': False
            #     },
            # }

        sku_id_list = cart_dict.keys()
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)

        for sku in sku_obj_list:
            # 添加需要额外返回的属性
            sku.count = cart_dict[sku.id]["count"]
            sku.selected = cart_dict[sku.id]["selected"]

        serializer = CartSKUSerializer(sku_obj_list, many=True)
        return Response(serializer.data)

    def put(self, request):
        """修改购物车中的商品"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data["sku_id"]
        count = serializer.validated_data["count"]
        selected = serializer.validated_data["selected"]

        try:
            user = request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            redis_conn = get_redis_connection("cart")
            pl = redis_conn.pipeline()
            pl.hset("cart_%s" % user.id, sku_id, count)

            if selected:
                pl.sadd("cart_selected_%s" % user.id, sku_id)
            else:
                pl.srem("cart_selected_%s" % user.id, sku_id)
            pl.execute()

            return Response(serializer.data)
        else:
            cookie_cart = request.COOKIES.get("cart")
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}

            response = Response(serializer.data)

            if sku_id in cart_dict:
                # 如果要修改的商品在cookie的字典中，赋值
                cart_dict[sku_id] = {
                    "count": count,
                    "selected": selected
                }
                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()

                response.set_cookie("cart", cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)

            return response

    def delete(self, request):
        """删除购物车中的商品"""
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data["sku_id"]

        try:
            user = request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            redis_conn = get_redis_connection("cart")
            pl = redis_conn.pipeline()
            pl.hdel("cart_%s" % user.id, sku_id)
            pl.srem("cart_selected_%s" % user.id, sku_id)
            pl.execute()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            cookie_cart = request.COOKIES.get("cart")

            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}

            response = Response(status=status.HTTP_204_NO_CONTENT)

            if sku_id in cart_dict:
                del cart_dict[sku_id]
                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie("cart", cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)

            return response


class CartSelectAllView(GenericAPIView):
    """购物车全部商品勾选/取消勾选状态"""
    serializer_class = CartSelectAllSerializer

    def perform_authentication(self, request):
        pass

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data["selected"]

        try:
            user = request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            redis_conn = get_redis_connection("cart")

            redis_cart = redis_conn.hgetall("cart_%s" % user.id)
            sku_id_list = redis_cart.keys()

            if selected:
                redis_conn.sadd("cart_selected_%s" % user.id, *sku_id_list)
            else:
                redis_conn.srem("cart_selected_%s" % user.id, *sku_id_list)

            return Response({"message": "OK"}, status=status.HTTP_200_OK)
        else:
            cookie_cart = request.COOKIES.get("cart")
            if cookie_cart:
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}

            response = Response({"message": "OK"})
            if cart_dict:
                for count_selected_dict in cart_dict.values():
                    count_selected_dict["selected"] = selected

                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie("cart", cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)

            return response
