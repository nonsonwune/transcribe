# celery_app.py
from celery import Celery
from config import Config


def make_celery(app_name=__name__):
    celery = Celery(
        app_name,
        backend=Config.CELERY_RESULT_BACKEND,
        broker=Config.CELERY_BROKER_URL,
    )
    celery.conf.update(Config.__dict__)
    return celery


celery = make_celery()
