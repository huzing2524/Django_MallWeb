from django.db import models
from meiduo_mall.utils.models import BaseModel

# Create your models here.


class OAuthQQUser(BaseModel):
    """QQ登录用户模型类"""
    # 进行外键关联的时候如果不是用一个应用，需要指定模型所在的应用名
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, verbose_name="用户")  # 级联方式删除，会一起删除外键关联字段的值
    openid = models.CharField(max_length=64, verbose_name="openid", db_index=True)  # 建立索引

    class Meta:
        db_table = "tb_oauth_qq"
        verbose_name = "QQ登录用户数据"
        verbose_name_plural = verbose_name
