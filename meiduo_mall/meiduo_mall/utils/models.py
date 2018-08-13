# -*- coding: utf-8 -*-
from django.db import models


class BaseModel(models.Model):
    """为模型类添加可以公用的父类字段"""
    # auto_now_add=True 创建模型的时候自动添加当前时间作为字段的值
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    # auto_now=True 更新模型的时候自动添加当前时间作为字段的值
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # 说明该类是抽象模型类，只用于继承使用，数据库迁移时不会创建BaseModel的数据表
        abstract = True

