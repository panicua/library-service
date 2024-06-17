import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LibraryService.settings")

app = Celery("LibraryService")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "your_task_name": {
        "task": "borrowing_app.tasks.borrowing_overdue",
        "schedule": crontab(hour=13, minute=00),
    },
}
