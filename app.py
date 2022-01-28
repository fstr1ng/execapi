from celery import Celery
from flask import Flask, request
import paramiko
import time, socket

def make_celery(app):
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
    return celery

app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

celery = make_celery(app)

@celery.task()
def exec_command(user, host, command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host, username=user)
    command += "\n"
    with ssh_client.invoke_shell() as ssh:
        time.sleep(0.5)
        ssh.recv(3000)
        ssh.send(command)
        ssh.settimeout(10)
        answer = ''
        while True:
            try:
                part = ssh.recv(4096).decode('utf-8')
                answer += part
                time.sleep(0.5)
            except socket.timeout:
                break
        return answer
    
@app.route('/', methods=['POST'])
def exec_endpoint():
    data = request.get_json()
    task = exec_command.delay(data['user'], data['host'], data['command'])
    return data
