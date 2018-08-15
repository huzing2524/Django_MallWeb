from django.shortcuts import render

# Create your views here.
# GET /areas/
# GET /areas/(?P<pk>\d+)/
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas import serializers
from areas.models import Area


class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """
    省市区三级联动视图集
    1.使用CacheResponseMixin为视图集同时补充List和Retrieve两种缓存，让第一次从mysql中查询后结果保存到redis缓存中，
    下次查询同样的数据，不会执行视图类和查询数据库，直接从缓存中返回，提高查询速度，减少数据库查询次数；
    2.根据__mro__多继承搜索顺序，必须先继承CacheResponseMixin，否则缓存查询不会起作用
    """
    pagination_class = None  # 关闭分页查询

    def get_queryset(self):
        """重写查询集方法，根据不同的查询方法返回不同的查询集范围"""
        if self.action == "list":
            return Area.objects.filter(parent=None)  # 省、直辖市
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            #  GET /areas/  {'get': 'list'}
            return serializers.AreaSerializer
        else:
            # self.action == "retrieve"
            # GET /areas/(?P<pk>\d+)/   {'get': 'retrieve'}
            return serializers.SubAreaSerializer

