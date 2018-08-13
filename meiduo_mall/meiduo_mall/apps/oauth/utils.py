# -*- coding: utf-8 -*-
import json
import logging
import urllib.parse
from urllib.request import urlopen
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from django.conf import settings  # 无论项目的配置文件在哪里，都可以从conf中提取出配置文件中的参数
from oauth import constants
from oauth.exceptions import OAuthQQAPIError

logger = logging.getLogger("django")


class OAuthQQ(object):
    """自定义QQ认证工具类"""

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        """
        QQ登录通用需要的参数: http://wiki.connect.qq.com/%E4%BD%BF%E7%94%A8authorization_code%E8%8E%B7%E5%8F%96access_token
        每个实例化对象中的参数都是独立隔离的；放在类属性中会共享，彼此影响
        :param client_id:申请QQ登录成功后，分配给应用的appid。
        :param client_secret:申请QQ登录成功后，分配给网站的appkey。
        :param redirect_uri:成功授权后的回调地址，必须是注册appid时填写的主域名下的地址，建议设置为网站首页或网站的用户中心。注意需要将url进行URLEncode。
        :param state:用来在query_params中存放在next后面客户端要回调的url地址
        """
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE

    def get_login_url(self):
        """
        获取qq登录的网址，把请求需要的参数拼接到url的查询字符串后面
        :return: "login_url": "https://graph.qq.com/oauth2.0/show
        ?which=Login&display=pc&response_type=code&client_id=101474184&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8080%2Foauth_callback.html&state=%2F&scope=get_user_info"
        """
        url = "https://graph.qq.com/oauth2.0/authorize?"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": self.state
        }
        # 将字典转换为url路径中的查询字符串
        url += urllib.parse.urlencode(params)
        # http://graph.qq.com/demo/index.jsp?code=9A5F******06AF&state=test
        return url

    def get_access_token(self, code):
        """
        服务器向QQ服务器请求
        :param code: 携带step:1中用户向QQ服务器请求得到的授权code
        :return:
        step2: 凭借授权code向QQ服务器请求access_token
        """
        url = "https://graph.qq.com/oauth2.0/token?"
        params = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        url += urllib.parse.urlencode(params)

        try:
            resp = urlopen(url)  # url请求
            # 读取响应体数据
            resp_data = resp.read()  # bytes
            resp_data = resp_data.decode()  # str
            # "access_token=FE04******CCE2&expires_in=7776000&refresh_token=88E4******BE14"

            # 将qs查询字符串格式数据转换为python的字典
            resp_dict = urllib.parse.parse_qs(resp_data)
        except Exception as e:
            logger.error("获取access_token异常：%s" % e)
            raise OAuthQQAPIError
        else:
            # {"access_token": "FE04******CCE2", "expires_in": "7776000", "refresh_token": "88E4******BE14"}
            access_token = resp_dict.get("access_token")
            return access_token[0]  # 列表，取索引得到str

    def get_openid(self, access_token):
        """
        :param access_token: step3: 凭借access_token向QQ服务器请求openid(唯一对应用户身份的标识)
        :return: callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );
        """
        url = "https://graph.qq.com/oauth2.0/me?access_token=" + access_token

        try:
            resp = urlopen(url)
            resp_data = resp.read()
            resp_data = resp_data.decode()
            resp_data = resp_data[10:-4]  # 字符串切割取出access_token
            resp_dict = json.loads(resp_data)
        except Exception as e:
            logger.error('获取openid异常：%s' % e)
            raise OAuthQQAPIError
        else:
            openid = resp_dict.get("openid")

            return openid

    def generate_bind_user_access_token(self, openid):
        """
        使用TimedJSONWebSignatureSerializer模块可以生成带有有效期的JWT
        :param openid: 必须传入
        :return: 用户以前用QQ绑定过账号，生成并返回，保存用户数据的token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        token = serializer.dumps({"openid": openid})  # bytes
        return token.decode()

    @staticmethod
    def check_bind_user_access_token(access_token):
        """
        使用TimedJSONWebSignatureSerializer模块可以校验JWT
        :param access_token:
        :return: 用户是第一次使用QQ登录，需要校验token，防止数据被篡改
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            return data["openid"]
