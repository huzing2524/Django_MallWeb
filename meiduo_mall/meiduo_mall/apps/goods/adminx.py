# -*- coding: utf-8 -*-
import xadmin
from xadmin import views

from goods import models


class BaseSetting(object):
    "xadmin的基本配置"
    enable_themes = True  # 开启主题切换功能
    use_bootswatch = True


class GlobalSettings(object):
    """xadmin的全局配置"""
    site_title = "美多商城运营管理系统"  # 设置站点标题
    site_footer = "美多商城集团有限公司"  # 设置站点的页脚
    menu_style = "accordion"  # 设置菜单折叠


class SKUAdmin(object):
    list_display = ["id", "name", "price", "stock", "sales", "comments"]  # 显示的字段
    list_editable = ["price", "stock"]  # 可编辑的字段
    search_fields = ["id", "name"]  # 搜索字段
    model_icon = "fa fa-gift"  # 图标
    list_filter = ["category"]  # 过滤器 过滤查询字段
    show_detail_fields = ["name"]  # 可以显示详情的字段
    show_bookmarks = True  # 开启显示书签功能
    list_export = ["xls", "csv", "xml"]  # 可以把数据输出为指定格式的文档，注意：导出到xls（excel) 需要安装xlwt扩展
    readonly_fields = ['sales', 'comments']  # 只读字段


class SKUSpecificationAdmin(object):
    def save_models(self):
        """保存数据对象"""
        obj = self.new_obj
        obj.save()

        # 补充自定义的异步任务
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self):
        """删除数据对象"""
        obj = self.obj
        sku_id = obj.sku.id
        obj.delete()

        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


class SKUImageAdmin(object):
    def save_models(self):
        obj = self.new_obj
        obj.save()

        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 设置SKU默认图片
        sku = obj.sku
        if not sku.default_image_url:
            # http://image.meiduo.site:8888/groupxxxxxx
            sku.default_image_url = obj.image.url
            sku.save()

    def delete_model(self):
        obj = self.obj
        sku_id = obj.sku.id
        obj.delete()

        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)

xadmin.site.register(models.GoodsCategory)
xadmin.site.register(models.GoodsChannel)
xadmin.site.register(models.Goods)
xadmin.site.register(models.Brand)
xadmin.site.register(models.GoodsSpecification)
xadmin.site.register(models.SpecificationOption)
xadmin.site.register(models.SKU, SKUAdmin)
xadmin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
xadmin.site.register(models.SKUImage)
