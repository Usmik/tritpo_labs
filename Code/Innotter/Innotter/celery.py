import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Innotter.settings')

app = Celery('Innotter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
