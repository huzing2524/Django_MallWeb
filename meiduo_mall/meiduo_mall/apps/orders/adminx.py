# -*- coding: utf-8 -*-
import xadmin

from orders.models import OrderInfo


class OrderInfoAdmin(object):
    """订单信息折线图"""
    model_icon = "fa fa-shopping-cart"  # 图标
    refresh_times = [3, 5]  # 可选以支持按多长时间(秒)刷新页面
    # title 控制图标名称
    # x-field 控制x轴字段
    # y-field 控制y轴字段，可以是多个值
    # title 控制图标名称；x-field 控制x轴字段；y-field 控制y轴字段，可以是多个值；order 控制默认排序
    data_charts = {
        "order_amount": {"title": "订单金额", "x-field": "create_time", "y-field": ("total_amount",),
                         "order": ("create_time",)},
        "order_count": {"title": "订单量", "x-field": "create_time", "y-field": ("total_count",),
                        "order": ("create_time",)}
    }


xadmin.site.register(OrderInfo, OrderInfoAdmin)
