import json
import redis

from django.conf import settings
from django.utils.translation import ugettext as _


EVENT_CHOICES = {
    1: _('New Task has been registrated'),
    2: _('Create new action with task'),
    3: _('Task successfully closed'),
    4: _('New user is activated')
}

ACTION_CHOICES = {
    1: _('Answer'),
    2: _('Comment'),
    3: _('Addition'),
    4: _('File')
}


def get_choices(choices, key):
    """ Python version Switch

    Return from dictionary value by key, default return empty string

    Args:
        choices {dict} -- dictionary of choices
        key {int} -- key of dictionary

    Returns:
        string -- valur of choices, default return empty string
    """
    return choices.get(key, '')


def prepare_and_create_log(event, user, task,
                           action, variable=settings.REDIS_VAR):
    """Create log for superuser

        This function push in Redis database json object with
    information about action

    Args:
        event {str} -- information about event log
        user {str[slug]} -- information about log's owner
        task {str[slug]} -- information about log's task
        action {str} -- detail information about log's action

    Needs:
        REDIS_VAR {str} -- key for store json object
        CELERY_REDIS_HOST {str} -- Redis host
        CELERY_REDIS_PORT {str} -- Redis port
        CELERY_REDIS_DB {str} -- Redis DB
    """
    data = {
        'event': get_choices(EVENT_CHOICES, event),
        'user': user,
        'task': task,
        'action': get_choices(ACTION_CHOICES, action)
    }
    r = redis.StrictRedis(
        host=settings.CELERY_REDIS_HOST,
        port=settings.CELERY_REDIS_PORT,
        db=settings.CELERY_REDIS_DB
    )
    r.rpush(variable, json.dumps(data))
