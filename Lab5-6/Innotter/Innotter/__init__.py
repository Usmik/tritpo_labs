from Innotter.celery import app as celery_app
from Innotter.pika_di import pika_di


__all__ = ('celery_app',)
pika_di()
