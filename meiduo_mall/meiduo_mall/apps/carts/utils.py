# -*- coding: utf-8 -*-
import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    """
    合并cookie中购物车的商品到redis购物车中，以cookie数据为主，覆盖redis中的数据
    :param request: 用户的请求对象
    :param user: 当前登录的用户
    :param response: 响应对象，用于清除购物车cookie
    :return: response
    """
    cookie_cart = request.COOKIES.get("cart")
    if not cookie_cart:
        return response
    cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))

    redis_conn = get_redis_connection("cart")
    redis_cart = redis_conn.hgetall("cart_%s" % user.id)

    cart = {}
    for sku_id, count in redis_cart.items():
        cart[int(sku_id)] = int(count)  # bytes——>int

    redis_cart_selected_add = []  # 记录最终要勾选的商品sku_id
    redis_cart_selected_remove = []  # 记录最终要取消勾选的商品sku_id

    for sku_id, count_selected_dict in cookie_cart_dict.items():
        # 把cookie中的商品skuid: count设置到redis列表中，覆盖了原有值
        cart[sku_id] = count_selected_dict["count"]

        if count_selected_dict["selected"]:
            redis_cart_selected_add.append(sku_id)
        else:
            redis_cart_selected_remove.append(sku_id)

    if cart:
        pl = redis_conn.pipeline()
        # 把cookie中的sku_id: count写入到redis中
        pl.hmset("cart_%s" % user.id, cart)

        if redis_cart_selected_add:
            pl.sadd("cart_selected_%s" % user.id, *redis_cart_selected_add)
        if redis_cart_selected_remove:
            pl.srem("cart_selected_%s" % user.id, *redis_cart_selected_remove)
        pl.execute()

    response.delete_cookie("cart")  # 删除cookie中购物车数据
    return response
