import uuid

from flask import request

from app import app, db
from app.models import Task
from app.tasks import exec_task, update_task_in_db

@app.route('/', methods=['POST'])
def exec_endpoint():
    data = request.get_json()
    data['id'] = uuid.uuid4().hex
    database_task = Task(id=data['id'], host=data['host'], user=data['user'], command=data['command'], status='new', result='')
    db.session.add(database_task)
    db.session.commit()
    celery_task = exec_task.apply_async(
            (data['user'], data['host'], data['command']),
            task_id=data['id'],
            link=update_task_in_db.s()
            )
    return data
