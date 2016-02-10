from celery.decorators import periodic_task
from datetime import timedelta


@periodic_task(run_every=(timedelta(seconds=3)))
def celery_task():
    print 'hello'
