"""Background tasks for celery queue manager"""
import time
import socket

import paramiko

from app import celery, db
from app.models import Task, Host


@celery.task()
def create_exec_task(_id, host, command):
    """Starts an execution of remote command.
    Database entry for command already exists at this point."""
    database_host = Host.query.filter_by(name=host).first()
    database_task = Task.query.filter_by(id=_id).first()
    database_task.status = "running"
    database_task.host = database_host.id
    db.session.commit()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(
            hostname=database_host.address,
            username=database_host.user,
            banner_timeout=200,
            key_filename="/root/.ssh/id_rsa_execapi",
        )
    except paramiko.SSHException:
        return "Connection failed"
    command += "\n"
    with ssh_client.invoke_shell() as ssh:
        time.sleep(0.5)
        ssh.recv(3000)
        ssh.send(command)
        ssh.settimeout(10)
        answer = ""
        while True:
            try:
                part = ssh.recv(4096).decode("utf-8")
                answer += part
                time.sleep(0.5)
            except socket.timeout:
                break
        return answer


@celery.task()
def callback_update_exec(result, _id, status):
    """Updates database entry after command execution end"""
    database_task = Task.query.filter_by(id=_id).first()
    database_task.status = status
    database_task.result = result
    db.session.commit()
    return status


@celery.task()
def create_host_task(name, address, user):
    """Adds host enty into database"""
    database_host = Host(name=name, address=address, user=user)
    db.session.add(database_host)
    db.session.commit()
    return database_host.id
