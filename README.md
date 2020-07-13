### Django_MallWeb
- 启动文件:
    Django_MallWeb/meiduo_mall/manage.py

- 运行参数:
    python3 manage.py runserver 127.0.0.1:8000

- 运行环境:
    - Ubuntu 18.04 LTS
    - Python 3.6.9
    - Django 1.11.11
    - Mysql 5.7.30

- 数据库:
    - 创建数据库: `create database meiduo_mall default charset=utf8;`
    - 创建新用户: 
        - `create user meiduo identified by 'meiduo'; `
        - `grant all on meiduo_mall.* to 'meiduo'@'%'; `
        - `flush privileges;`
    - 数据库迁移:
        - 生成迁移文件: `python3 meiduo_mall/manage.py makemigrations`
        - 生成数据表: `python3 meiduo_mall/manage.py migrate`

- 前端:
    - `node.js` 和 `npm工具`
    - 安装live-server: `npm install -g live-server`
    - 启动前段界面, 在静态文件目录front_end_pc下执行；
        - `cd front_end_pc/`
        - `live-server`

- issues:
    - Python解释器版本, Django版本, xadmin版本 有相互对应的关系，选择不合适的版本会报错。
    - xadmin: https://github.com/sshwsfc/xadmin/tarball/master
    - xadmin: 官方版本对Python3的高版本不兼容, xadmin2需要Django2.2以上的版本
    - 最好Docker打包生成一个容器运行, 解决以上问题