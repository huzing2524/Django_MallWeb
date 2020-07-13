### Django_MallWeb
- 启动文件:
    Django_MallWeb/meiduo_mall/manage.py

- 运行参数:
    python3 manage.py runserver 127.0.0.1:8000

- 运行环境:
    - Ubuntu 18.04 LTS
    - Python 3.6.9
    - Mysql 5.7.30

- issues:
    - Python解释器版本, Django版本, xadmin版本 有相互对应的关系，选择不合适的版本会报错。
    - xadmin: https://github.com/sshwsfc/xadmin/tarball/master
    - xadmin: 官方版本对Python3的高版本不兼容, xadmin2需要Django2.2以上的版本
    - 最好Docker打包生成一个容器运行, 解决以上问题