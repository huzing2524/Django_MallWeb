from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from meiduo_mall.utils.models import BaseModel
from users import constants


class User(AbstractUser):
    """用户模型类，继承AbstractUser认证、权限系统中用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name="邮箱验证状态")
    # 默认收货地址设置为外键，关联的是另外一张表Address
    default_address = models.ForeignKey("Address", related_name="users", null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name="默认地址")

    class Meta:
        db_table = "tb_users"
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        """生成验证邮箱的激活url链接"""
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {
            "user_id": self.id,
            "email": self.email
        }
        # 把user_id和email字段都放进payload中加密生成token
        token = serializer.dumps(data).decode()
        verify_url = "http://127.0.0.1:8080/success_verify_email.html?token=" + token

        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        """邮箱url链接返回激活校验"""
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)  # 校验token是否正确
        except BadData:
            return None
        else:
            # token有效未被篡改，根据生成的时候嵌入的字段，在数据库中查询出用户
            user_id = data["user_id"]
            email = data["email"]
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user


class Address(BaseModel):
    """用户收货地址模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses", verbose_name="用户")
    title = models.CharField(max_length=20, verbose_name="地址名称")
    receiver = models.CharField(max_length=20, verbose_name="收货人")
    province = models.ForeignKey("areas.Area", on_delete=models.PROTECT, related_name="province_addresses",
                                 verbose_name="省")
    city = models.ForeignKey("areas.Area", on_delete=models.PROTECT, related_name="city_addresses", verbose_name="市")
    district = models.ForeignKey("areas.Area", on_delete=models.PROTECT, related_name="district_addresses",
                                 verbose_name="区")
    place = models.CharField(max_length=50, verbose_name="地址")
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    tel = models.CharField(max_length=30, null=True, blank=True, default="", verbose_name="固定电话")
    email = models.CharField(max_length=30, null=True, blank=True, default="", verbose_name="电子邮箱")
    is_deleted = models.BooleanField(default=False, verbose_name="逻辑删除")

    class Meta:
        db_table = "tb_address"
        verbose_name = "用户地址"
        verbose_name_plural = verbose_name
        ordering = ["-update_time"]  # 指定默认按照更新时间倒序排列，字段继承而来
