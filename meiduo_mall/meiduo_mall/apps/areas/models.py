from django.db import models


# Create your models here.
class Area(models.Model):
    """省市区三级联动：创建省市区数据模型，采用自关联方式"""
    name = models.CharField(max_length=20, verbose_name="地名")
    # 第一个参数使用"self"，表明自关联字段的外键指向自身，on_delete删除主键时把关联的外键设置为Null
    # 因为有两级的外键"市"和"区"关联主键，所以使用related_name区分。area.subs查询出所有下属行政区划，而不再使用area.area_set
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="subs", null=True, blank=True,
                               verbose_name="上级行政区划")

    class Meta:
        db_table = "tb_areas"
        verbose_name = "行政区划"
        verbose_name_plural = "行政区划"

    def __str__(self):
        return self.name
