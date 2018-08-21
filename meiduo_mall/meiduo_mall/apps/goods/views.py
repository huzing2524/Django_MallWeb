from django.shortcuts import render
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from goods.models import SKU
from goods.serializers import SKUIndexSerializer, SKUSerializer


# GET /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
class SKUListView(ListAPIView):
    """商品三级菜单中全部商品列表"""
    serializer_class = SKUSerializer
    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ("create_time", "price", "sales")

    # utils中设置了全局分页

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class SKUSearchViewSet(HaystackViewSet):
    """SKU模型类全文检索视图集"""
    index_models = [SKU]
    serializer_class = SKUIndexSerializer
