# -*- coding: utf-8 -*-
# 开启celery任务，celery是分布式异步/同步任务队列调度框架，任务Task交给消息中间件Broker，然后任务执行单元Worker去Broker中领取任务执行
# ~/Desktop/Django_MallWeb/meiduo_mall 执行在celery_tasks目录中的main文件
# celery -A celery_tasks.main worker --loglevel=info

import logging
from celery_tasks.main import celery_app
from celery_tasks.sms.utils.yuntongxun.sms import CCP

logger = logging.getLogger("django")


@celery_app.task(name="send_sms_code")
def send_sms_code(mobile, sms_code, expires, temp_id):
    """
    使用celery发送短信验证码
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :param expires: 有效时间
    :return: None
    """
    try:
        ccp = CCP()
        # result = ccp.send_template_sms(mobile, [sms_code, expires], temp_id)
        result = 0
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        # 返回0 表示发送短信成功
        if result == 0:
            logger.info("发送验证码短信[正常][ 手机号: %s, 短信验证码: %s ]" % (mobile, sms_code))
        else:
            # logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
            pass
