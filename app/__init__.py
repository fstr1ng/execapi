from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery

app = Flask(__name__)    
app.config.update(    
    CELERY_BROKER_URL='redis://localhost:6379',    
    CELERY_RESULT_BACKEND='redis://localhost:6379',    
    SQLALCHEMY_DATABASE_URI='sqlite:///sqlite.db'    
    )

db = SQLAlchemy(app)

celery = Celery(
    app.import_name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL']
)
celery.conf.update(app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)
celery.Task = ContextTask

from app import routes, models, tasks
