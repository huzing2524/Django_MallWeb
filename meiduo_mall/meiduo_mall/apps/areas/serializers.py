# -*- coding: utf-8 -*-
from rest_framework import serializers

from areas.models import Area


class AreaSerializer(serializers.ModelSerializer):
    """省、直辖市序列化器"""

    class Meta:
        model = Area
        # "id":省份id, "name":省份名称
        fields = ("id", "name")


class SubAreaSerializer(serializers.ModelSerializer):
    """地级市、区县序列化器"""
    # 关联对象嵌套序列化:可以使查询集结果再次序列化显示出具体的地级市、区县信息，否则只会显示多个Area对象的id
    # many=True 关联的对象数据包含多个，一个省对应多个地级市
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        # "id":上级区划id(省份id或直辖市id), "name":上级区划(省份或直辖市)的名称, "subs":下属所有区划(地级市、区县)信息
        fields = ("id", "name", "subs")
