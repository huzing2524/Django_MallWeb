# -*- coding: utf-8 -*-
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods

logger = logging.getLogger("django")


class CartSKUSerializer(serializers.ModelSerializer):
    """订单商品详情序列化器"""
    count = serializers.IntegerField(label="数量")

    class Meta:
        model = SKU
        fields = ("id", "name", "default_image_url", "price", "count")


class OrderSettlementSerializer(serializers.Serializer):
    """订单结算序列化器"""
    freight = serializers.DecimalField(label="运费", max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)  # 嵌套序列化字段


class SaveOrderSerializer(serializers.ModelSerializer):
    """保存订单序列化器"""

    class Meta:
        model = OrderInfo
        fields = ("address", "pay_method", "order_id")
        read_only_fields = ("order_id",)
        extra_kwargs = {
            "address": {
                "write_only": True,
                "required": True
            },
            "pay_method": {
                "write_only": True,
                "required": True
            }
        }

    def create(self, validated_data):
        address = validated_data["address"]
        pay_method = validated_data["pay_method"]

        user = self.context["request"].user

        redis_conn = get_redis_connection("cart")
        redis_cart_dict = redis_conn.hgetall("cart_%s" % user.id)
        redis_cart_selected = redis_conn.smembers("cart_selected_%s" % user.id)

        cart = {}
        for sku_id in redis_cart_selected:
            cart[int(sku_id)] = int(redis_cart_dict[sku_id])  # {sku_id(16): count(2)}

        if not cart:
            # 没有商品被选中，提交订单时商品数量为0
            raise serializers.ValidationError("没有需要结算的商品")

        # 开启Django事务，确保数据库修改、新建订单一起成功/失败回滚
        with transaction.atomic():
            try:
                # 创建保存点，事务执行失败可以回滚到此处
                save_id = transaction.savepoint()
                # 根据配置信息的时区生成当前时间datetime对象
                order_id = timezone.now().strftime("%Y%m%d%H%M%S") + "%09d" % user.id
                # 创建订单记录
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal("0"),
                    freight=Decimal("10.00"),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM["UNSEND"] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        "CASH"] else OrderInfo.ORDER_STATUS_ENUM["UNPAID"]
                )
                sku_id_list = cart.keys()
                # 遍历需要结算的商品
                for sku_id in sku_id_list:
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        sku_count = cart[sku_id]  # 用户需要购买某件商品的数量
                        origin_stock = sku.stock  # 数据库中商品原始库存
                        origin_sales = sku.sales  # 数据库中商品原始销量

                        if origin_stock < sku_count:
                            # 商品库存不足，购买失败，回滚事务到保存点
                            transaction.savepoint_rollback(save_id)
                            raise serializers.ValidationError("商品%s库存不足" % sku.name)

                        import time
                        time.sleep(5)

                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count

                        # 并发处理，避免出现资源竞争问题，使用"乐观锁"，在更新的时候判断此时的库存是否是之前查询出的库存
                        # update返回受影响的行数
                        result = SKU.objects.filter(id=sku.id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)
                        if result == 0:
                            # 更新库存失败，出现资源竞争，结束本次循环后续流程，不会创建订单
                            continue

                        order.total_count += sku_count
                        order.total_amount += sku.price * sku_count

                        # 创建商品订单记录
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price
                        )
                        # 创建订单成功后跳出死循环，继续for循环创建下一件商品的订单记录
                        break

                order.save()
            except serializers.ValidationError:
                raise
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                raise
            else:
                # 提交从保存点到当前状态的所有数据库事务操作
                transaction.savepoint_commit(save_id)

        # 删除购物车中已提交生成订单的商品
        pl = redis_conn.pipeline()
        pl.hdel("cart_%s" % user.id, *redis_cart_selected)
        pl.srem("cart_selected_%s" % user.id, *redis_cart_selected)
        pl.execute()

        return order
