"""Simple API for remote command execution"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery


app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL=os.environ["CELERY_BROKER_URL"],
    CELERY_RESULT_BACKEND=os.environ["CELERY_RESULT_BACKEND"],
    SQLALCHEMY_DATABASE_URI=os.environ["SQLALCHEMY_DATABASE_URI"],
)

db = SQLAlchemy(app)

celery = Celery(
    app.import_name,
    backend=app.config["CELERY_RESULT_BACKEND"],
    broker=app.config["CELERY_BROKER_URL"],
)
celery.conf.update(app.config)


class ContextTask(celery.Task):
    """Custom Celery task"""

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask

from app import routes, models, tasks
