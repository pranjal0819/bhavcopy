import os

from celery import Celery
from celery.app.log import TaskFormatter
from celery.schedules import crontab
from celery.signals import after_setup_task_logger

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery("mysite", include=["mysite.tasks"])

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# app.autodiscover_tasks()

app.conf.timezone = "Asia/Kolkata"

app.conf.beat_schedule = {
    "refresh-data": {
        "task": "refresh_data",
        "schedule": crontab(
            minute=os.environ.get('SCHEDULE_MINUTE', '*'),
            hour=os.environ.get('SCHEDULE_HOUR', '*'),
            day_of_week=os.environ.get('SCHEDULE_DAY_OF_WEEK', '*')),
        "args": (),
    }
}


# Customise the celery.task log format

@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            TaskFormatter('[%(asctime)s: %(task_name)s]: %(message)s'))
