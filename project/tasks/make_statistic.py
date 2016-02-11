import redis
import json
from django.conf import settings


def switch_event(event):
    return {
        1: 'New Task has been registrated',
        2: 'Create new action with task',
        3: 'Task successfully closed'
    }.get(event, '')


def switch_action(action):
    return {
        1: 'Answer',
        2: 'Comment',
        3: 'Addition',
        4: 'File'
    }.get(action, '')


def log_super_action(event, user, task, action, variable=settings.REDIS_VAR):
    data = {
        'event': switch_event(event),
        'user': user,
        'task': task,
        'action': switch_action(action)
    }
    r = redis.StrictRedis(
        host=settings.CELERY_REDIS_HOST,
        port=settings.CELERY_REDIS_PORT,
        db=settings.CELERY_REDIS_DB
    )
    r.rpush(variable, json.dumps(data))
