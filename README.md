### Django_MallWeb
- 启动文件:
    Django_MallWeb/meiduo_mall/manage.py

- 运行参数:
    python3 manage.py runserver 127.0.0.1:8000

- 运行环境:
    - Ubuntu 18.04 LTS
    - Python 3.6.9
        - Django 1.11.11不支持Python 3.7及以上的版本
        - 由于下面句尾逗号的原因, django版本有bug
          ```
          Python38\lib\site-packages\django/contrib/admin/widgets.py", line 152
          
          '%s=%s' % (k, v) for k, v in params.items(),
          ^
          SyntaxError: Generator expression must be parenthesized
          ```   
    - Django 1.11.11
    - Mysql 5.7.30
    - Python第三方包, 在/path/Django_MallWeb的项目根目录下:
        - `pip3 install -r requirements.txt`
        - Fast DFS文件存储的客户端: `pip3 install meiduo_mall/meiduo_mall/utils/fastdfs/fdfs_client-py-master.zip`

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

- Docker:
    - 生成Docker镜像: 
        - 进入Dockerfile所在的文件夹 `cd path/Django_MallWeb`
        - `sudo docker build -t 镜像名称 .`
    - 启动镜像, 生成容器: `sudo docker run -it --name=容器名称 [镜像名称|镜像id] /bin/bash`
    - 进入容器内部: `sudo docker exec -it [容器名称|容器id] /bin/bash`
    - 启动Django服务器: `python3 meiduo_mall/manage.py runserver 0.0.0.0:8000`
    - Notes:
        - Docker容器内部数据库连接配置, 不能使用localhost/127.0.0.1, 要使用宿主机的ip地址. Docker容器内部本机ip地址为0.0.0.0
            ```config
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'HOST': '192.168.31.89',  # 改成宿主机ip地址或者宿主机docker0地址
                    'PORT': 3306,
                    'USER': 'meiduo',
                    'PASSWORD': 'meiduo',
                    'NAME': 'meiduo_mall'
                    }
            }
            ```
        - 宿主机访问容器内部应用程序Django服务器:
            - 在容器内找到ip地址: `ifconfig` (外部宿主机`ifconfig`列表显示的docker0的ip地址和容器内部ip地址不相同)
            - 在宿主机使用浏览器/postman通过上面的ip address:port访问容器内服务

- FastDFS分布式文件系统:
    - 拉取镜像: `docker image pull delron/fastdfs`
    - tracker: 
        - 负载均衡, 调度
        - `docker run -dti --network=host --name tracker -v /var/fdfs/tracker:/var/fdfs delron/fastdfs tracker`
    - storage: 
        - 文件存储
        - `docker run -dti --network=host --name storage -e TRACKER_SERVER=本机ip地址(不要使用127.0.0.1):22122 -v /var/fdfs/storage:/var/fdfs delron/fastdfs storage`
    - 查看所有容器: `sudo docker ps -a` 或者 `sudo docker ps --all`
    - 添加测试数据到FastDFS文件系统中:
        - 将/var/fdfs/storage中的data目录删除: `sudo rm -rf /var/fdfs/storage/data/`
        - 将data.tar.gz文件拷贝到/var/fdfs/storage中: `sudo cp data.tar.gz /var/fdfs/storage/`
        - 解压缩: `tar -zxvf data.tar.gz`

- xadmin:
    - Drop-in replacement of Django admin comes with lots of goodies, fully extensible with plugin support, pretty UI based on Twitter Bootstrap.
    - Django自带的后台管理网站是localhost:port/admin, xadmin是加强版的后台管理站点.
    - [xadmin](https://pypi.org/project/xadmin/): django >=1.9
    - [xadmin2](https://pypi.org/project/xadmin2/): django >=2 (Python>=3.7, django高版本使用xadmin会有问题)
    - 创建超级管理员账号: `python3 meiduo_mall/manage.py createsuperuser`

- Notes:
    - Python解释器版本, Django版本, xadmin版本 有相互对应的关系，选择不合适的版本会报错。
    - xadmin: https://github.com/sshwsfc/xadmin/tarball/master
    - xadmin: 官方版本对Python3的高版本不兼容, xadmin2需要Django2.2以上的版本
    - 最好Docker打包生成一个容器运行, 解决以上问题