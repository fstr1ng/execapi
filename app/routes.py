import uuid
import pdb

from flask import request, jsonify

from app import app, db
from app.models import Task, Host
from app.tasks import create_exec_task, callback_update_exec, create_host_task

@app.route('/host', methods=['GET','POST'])
@app.route('/host/<name>', methods=['GET','POST'])
def host_endpoint(name=None):
    if not name and request.method=='GET':
        all_hosts = Host.query.all()
        #pdb.set_trace()
        all_hosts_dicts = [host.__dict__ for host in all_hosts]
        for host in all_hosts_dicts:
            del host['_sa_instance_state']
        return jsonify(all_hosts_dicts)
    if not name and request.method=='POST':
        data = request.get_json()
        celery_task = create_host_task.apply_async(
            (data['name'], data['address'], data['user']))
        return celery_task.task_id, data



@app.route('/exec', methods=['POST'])
def exec_endpoint():
    data = request.get_json()
    task_id = uuid.uuid4().hex
    database_task = Task(
        id=task_id,
        command=data['command'],
        )
    db.session.add(database_task)
    db.session.commit()
    celery_task = create_exec_task.apply_async(
            (task_id, data['host'], data['command']),
            task_id=task_id,
            link=callback_update_exec.s(task_id,'done'),
            link_error=callback_update_exec.s(task_id, 'failed')
            )
    return data
