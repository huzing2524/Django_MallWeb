# -*- coding: utf-8 -*-
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """分页配置类"""
    # 每页数目
    page_size = 2
    # 前端访问指明每页数量的参数名，放在查询字符串中
    page_size_query_param = "page_size"
    # 限制前端获取每页数量的最大限制数目
    max_page_size = 20
