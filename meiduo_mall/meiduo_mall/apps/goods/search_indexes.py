# -*- coding: utf-8 -*-
from haystack import indexes

from goods.models import SKU

"""
手动生成初始索引
python manage.py rebuild_index
"""


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """SKU索引数据模型类，指明让搜索引擎对哪些字段建立索引"""
    # 字段的索引值可以由多个数据库模型类字段组成，使用模板文件来指明
    text = indexes.CharField(document=True, use_template=True)
    # model_attr 指明引用数据库模型类的特定字段
    id = indexes.IntegerField(model_attr="id")
    name = indexes.CharField(model_attr="name")
    price = indexes.DecimalField(model_attr="price")
    default_image_url = indexes.CharField(model_attr="default_image_url")
    comments = indexes.IntegerField(model_attr="comments")

    def get_model(self):
        """指明建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """指明模型类中需要建立索引的查询集范围"""
        return SKU.objects.filter(is_launched=True)  # 排除未上架商品
