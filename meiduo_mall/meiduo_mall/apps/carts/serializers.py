# -*- coding: utf-8 -*-
from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """购物车商品序列化器"""
    sku_id = serializers.IntegerField(label="商品id", min_value=1)
    count = serializers.IntegerField(label="数量", min_value=1)
    selected = serializers.BooleanField(label="是否勾选", default=True)

    def validate(self, data):
        try:
            sku = SKU.objects.get(id=data["sku_id"])
        except SKU.DoesNotExist:
            return serializers.ValidationError("商品不存在")

        if data["count"] > sku.stock:
            raise serializers.ValidationError("商品库存不足")

        return data


class CartSKUSerializer(serializers.ModelSerializer):
    """购物车商品查询序列化器"""
    count = serializers.IntegerField(label="数量")
    selected = serializers.BooleanField(label="是否勾选")

    class Meta:
        model = SKU
        fields = ("id", "count", "name", "default_image_url", "price", "selected")


class CartDeleteSerializer(serializers.Serializer):
    """购物车删除商品序列化器"""
    sku_id = serializers.IntegerField(label="商品id", min_value=1)

    def validate_sku_id(self, value):
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("该商品不存在")

        return value


class CartSelectAllSerializer(serializers.Serializer):
    """购物车全部商品勾选/取消勾选状态 序列化器"""
    selected = serializers.BooleanField(label="是否勾选")
