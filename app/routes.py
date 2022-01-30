import uuid
import pdb

from flask import request, jsonify

from app import app, db
from app.models import Task, Host
from app.tasks import create_exec_task, callback_update_exec, create_host_task


@app.route('/host', methods=['GET','POST'])
def host_all_endpoint(name=None):
    ''' GET returns all hosts
        POST creates new host '''
    if request.method=='GET':
        all_hosts = Host.query.all()
        #pdb.set_trace()
        all_hosts_dicts = [host.__dict__ for host in all_hosts]
        for host in all_hosts_dicts:
            del host['_sa_instance_state']
        return jsonify(all_hosts_dicts)
    if request.method=='POST':
        data = request.get_json()
        celery_task = create_host_task.apply_async(
            (data['name'], data['address'], data['user']))
        return celery_task.task_id, data

@app.route('/host/<name>', methods=['GET','POST'])
def host_one_endpoint(name):
    ''' GET returns exact host
        POST edits existing host '''
    if request.method=='GET':
        database_host = Host.query.filter_by(name=name).first()
        host_dict = database_host.__dict__
        del host_dict['_sa_instance_state']
        return jsonify(host_dict)
    if request.method=='POST':
        database_host = Host.query.filter_by(name=name).first()
        data = request.get_json()
        pdb.set_trace()
        for key in data:
            try:
                database_host.__getattribute__(key)
                database_host.__setattr__(key, data[key])
                host_dict = database_host.__dict__
                del host_dict['_sa_instance_state']
                return jsonify(host_dict)
            except AttributeError:
                return {'error': 'no such attribute'}


@app.route('/exec', methods=['GET', 'POST'])
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

