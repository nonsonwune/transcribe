from celery import Celery
from config import Config
from flask import Flask
from utils import setup_directories
import tasks  # Ensure tasks module is imported


def make_celery(app=None):
    if app is None:
        app = Flask(__name__)
        app.config.from_object(Config)
        with app.app_context():
            setup_directories(app)

    celery = Celery(
        app.import_name,
        backend=app.config["RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app_with_celery():
    app = Flask(__name__)
    app.config.from_object(Config)
    with app.app_context():
        setup_directories(app)

    celery = make_celery(app)
    celery.conf.broker_connection_retry_on_startup = True

    return app, celery


# Initialize Flask app and Celery instance
app, celery = create_app_with_celery()
