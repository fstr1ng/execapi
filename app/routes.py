"""Flask routes (API endpoints)"""
import uuid

from flask import request, jsonify

from app import app, db
from app.models import Task, Host
from app.tasks import create_exec_task, callback_update_exec, create_host_task


def get_entities_from_db(database_class):
    """Input: SQLAlchemy Class. Output: dictioany for json answers"""
    all_entities = database_class.query.all()
    all_entities_dict = [entity.__dict__ for entity in all_entities]
    for entity in all_entities_dict:
        del entity["_sa_instance_state"]
    return all_entities_dict


@app.route("/host", methods=["GET", "POST"])
def host_all_endpoint():
    """GET returns all hosts
    POST creates new host"""
    if request.method == "GET":
        entities = get_entities_from_db(Host)
        return jsonify(entities)
    if request.method == "POST":
        data = request.get_json()
        celery_task = create_host_task.apply_async(
            (data["name"], data["address"], data["user"])
        )
        data["task_id"] = celery_task.task_id
        return jsonify(data)


@app.route("/host/<name>", methods=["GET", "POST"])
def host_one_endpoint(name):
    """GET returns exact host
    POST edits existing host"""
    if request.method == "GET":
        database_host = Host.query.filter_by(name=name).first()
        host_dict = database_host.__dict__
        del host_dict["_sa_instance_state"]
        return jsonify(host_dict)
    if request.method == "POST":
        database_host = Host.query.filter_by(name=name).first()
        data = request.get_json()
        for key in data:
            try:
                database_host.__getattribute__(key)
                database_host.__setattr__(key, data[key])
                host_dict = database_host.__dict__
                del host_dict["_sa_instance_state"]
                db.session.commit()
                return jsonify(host_dict)
            except AttributeError:
                return jsonify({"error": "no such attribute"})


@app.route("/exec", methods=["GET", "POST"])
def exec_endpoint():
    """GET returns all exec tasks
    POST creates new exec task"""
    if request.method == "GET":
        return jsonify(get_entities_from_db(Task))
    if request.method == "POST":
        data = request.get_json()
        task_id = uuid.uuid4().hex
        database_task = Task(
            id=task_id,
            command=data["command"],
        )
        db.session.add(database_task)
        db.session.commit()
        celery_task = create_exec_task.apply_async(
            (task_id, data["host"], data["command"]),
            task_id=task_id,
            link=callback_update_exec.s(task_id, "done"),
            link_error=callback_update_exec.s(task_id, "failed"),
        )
        data["task_id"] = celery_task.task_id
        return data
