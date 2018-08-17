from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from goods import serializers
from goods.models import SKU


# GET /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
class SKUListView(ListAPIView):
    """商品三级菜单中全部商品列表"""
    serializer_class = serializers.SKUSerializer
    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ("create_time", "price", "sales")

    # utils中设置了全局分页

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        return SKU.objects.filter(category_id=category_id, is_launched=True)
