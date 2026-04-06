import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kinoafisha.settings')

app = Celery('kinoafisha')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-new-movies-every-night': {
        'task': 'main_page.tasks.check_new_movies',
        'schedule': crontab(minute='*/15'),
    },
    'delete-old-sessions-every-15-min': {
        'task': 'main_page.tasks.delete_old_sessions',
        'schedule': crontab(minute='*/15'),
    },
}

app.conf.timezone = 'Asia/Yekaterinburg'
