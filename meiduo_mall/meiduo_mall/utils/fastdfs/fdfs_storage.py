# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client


@deconstructible
class FastDFSStorage(Storage):
    def __init__(self, base_url=None, client_conf=None):
        """
        :param base_url: 用于构造图片完整路径使用，图片服务器的域名
        :param client_conf: FastDFS客户端配置文件的路径
        """
        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url

        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

    def _open(self, name, mode="rb"):
        """用不到打开文件(交给docker镜像中的nginx处理了)，所以pass，但是必须得有这个方法"""
        pass

    def _save(self, name, content):
        """
        在FastDFS中保存文件
        :param name: 传入的文件名
        :param content: 文件内容
        :return: 保存到数据库中的FastDFS的文件名
        """
        client = Fdfs_client(self.client_conf)

        """
        >>> ret
        {'Group name': 'group1', 'Remote file_id': 'group1/M00/00/02/CtM3BVr-k6SACjAIAAJctR1ennA809.png', 
        'Status': 'Upload successed.', 'Local file name': '/Users/delron/Desktop/1.png', 
        'Uploaded size': '151.00KB', 'Storage IP': '10.211.55.5'}
        """
        # 传入文件bytes数据，取出文件名后缀png
        ret = client.upload_by_buffer(content.read(), file_ext_name=name.split('.')[-1])

        if ret.get("Status") != "Upload successed.":
            raise Exception("upload file failed")

        file_name = ret.get("Remote file_id")
        return file_name

    def exists(self, name):
        """
        判断文件是否存在，FastDFS可以自行解决文件的重名问题，所以此处返回False，告诉Django上传的都是新文件
        :param name: 文件名
        :return: False
        """
        return False

    def url(self, name):
        """
        返回文件的完整URL路径，在使用ImageField的 url属性的时候，这个方法会被调用
        :param name: 数据库中保存的文件名
        :return: 完整的URL
        """
        return self.base_url + name
