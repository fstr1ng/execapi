import time, socket

import paramiko

from app import celery

@celery.task()
def exec_task(user, host, command):
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
 
@celery.task()
def update_task_in_db(result):
    pass

