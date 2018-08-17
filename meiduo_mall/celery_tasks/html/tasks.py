# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.template import loader

from celery_tasks.main import celery_app
from goods.models import SKU
from goods.utils import get_categories


@celery_app.task(name="generate_static_sku_detail_html")
def generate_static_sku_detail_html(sku_id):
    """
    生成静态商品详情页面
    :param sku_id: 商品sku_id
    :return: html文件
    """
    # 商品分类菜单
    categories = get_categories()

    # 获取当前sku对象的信息
    sku = SKU.objects.get(id=sku_id)
    sku.images = sku.skuimage_set.all()

    # 面包屑导航信息中的频道
    goods = sku.goods
    goods.channel = goods.category1.goodschannel_set.all()[0]

    # 当前商品的规格
    sku_specs = sku.skuspecification_set.order_by("spec_id")

    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    # 获取当前商品的所有SKU
    skus = goods.sku_set.all()

    # 构建不同规格选项的sku字典
    """
    spec_sku_map = {
        (颜色， 版本): 9
        (13, 20): 9,
        (13, 21): 12,
        (14, 20): 13
    }
    """
    spec_sku_map = {}

    for s in skus:
        # 获取sku的规格参数
        # s_specs =[{spec_id: 6 颜色, option: 14 蓝色}, {spec_id: 7 版本, options: 21 128G}]
        s_specs = s.skuspecification_set.order_by("spec_id")

        key = []
        for spec in s_specs:
            # key = [14, 21]
            key.append(spec.option.id)

        spec_sku_map[tuple(key)] = s.id

    """
    specs = [
       {
           'name': '屏幕尺寸',
           'options': [
               {'value': '13.3寸', 'sku_id': xxx},
               {'value': '15.4寸', 'sku_id': xxx},
           ]
       },
       {
           'name': '颜色',
           'options': [
               {'value': '银色', 'sku_id': xxx},
               {'value': '黑色', 'sku_id': xxx}
           ]
       },
       ...
    ]
    """
    # 获取当前商品的规格信息
    specs = goods.goodsspecification_set.order_by("id")

    # 如果当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(specs):
        return

    # index=0, spec = {name: 颜色}
    # enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标，一般用在for循环当中
    for index, spec in enumerate(specs):
        # 复制当前sku的规格键
        # sku_key = [13, 20], key = [13, 20]
        key = sku_key[:]

        # 该规格的选项
        # options = [{value: 蓝, id: 14}, {value: 金, id: 13}, {value: 红, id: 15}]
        options = spec.specificationoption_set.all()

        for option in options:
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            # option {value: 蓝 id 14, sku_id:13}
            option.sku_id = spec_sku_map.get(tuple(key))

        # spec = {name: 颜色, options:[{value: 金 id 13}, {value: 蓝 id 14}, {value: 红 id 15}]}
        spec.options = options

    # 渲染模板，生成静态html文件
    context = {
        "categories": categories,
        "goods": goods,  # SPU
        "specs": specs,  # 规格
        "sku": sku
    }

    template = loader.get_template("detail.html")
    html_text = template.render(context)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/' + str(sku_id) + '.html')

    # /front_end_pc/goods/1.html
    with open(file_path, "w") as f:
        f.write(html_text)
