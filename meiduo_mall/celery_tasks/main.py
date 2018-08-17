# -*- coding: utf-8 -*-
from celery import Celery
import os

"""
开启celery任务，celery是分布式异步/同步任务队列调度框架，任务Task交给消息中间件Broker，然后任务执行单元Worker去Broker中领取任务执行
~/Desktop/Django_MallWeb/meiduo_mall 执行在celery_tasks目录中的main文件
celery -A celery_tasks.main worker --loglevel=info
"""

# 为celery使用django配置文件进行设置
if not os.getenv("DJANGO_SETTINGS_MODULE"):
    os.environ["DJANGO_SETTINGS_MODULE"] = "meiduo_mall.settings.dev"

# 创建celery应用
celery_app = Celery("meiduo")

# 导入celery应用
celery_app.config_from_object("celery_tasks.config")

# 自动注册celery任务
celery_app.autodiscover_tasks(["celery_tasks.sms", "celery_tasks.email", "celery_tasks.html"])
