from celery.decorators import periodic_task
from celery.schedules import crontab

from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives

import redis
import json


@periodic_task(run_every=(crontab(minute='*/1')))
def send_super_statistic():
    r = redis.StrictRedis(
        host=settings.CELERY_REDIS_HOST,
        port=settings.CELERY_REDIS_PORT,
        db=settings.CELERY_REDIS_DB
    )

    redis_key = settings.REDIS_VAR
    obj_len = r.llen(redis_key)

    subject = 'Data reporting'
    from_email = settings.EMAIL_HOST_USER

    if obj_len:
        print 'not null'
        object_list = []

        row_object_list = r.lrange(redis_key, 0, obj_len-1)
        for obj in row_object_list:
            object_list.append(json.loads(obj))

        htmly = get_template('addition_page/email_super_statistic.html')
        text_content = htmly.render(Context({'object_list': object_list}))

        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            settings.EMAIL_SUPERUSERS
        )
        msg.attach_alternative(text_content, 'text/html')

        msg.send()

        r.ltrim(redis_key, obj_len, -1)

    else:
        print 'null'
