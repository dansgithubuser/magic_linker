from datetime import datetime, timezone
import os
import subprocess
import time

DIR = os.path.dirname(os.path.realpath(__file__))
REPO_DIR = os.path.dirname(DIR)
COMMANDS_DIR = os.path.join(REPO_DIR, 'commands')
COMMANDS = [i for i in os.listdir(COMMANDS_DIR) if i.endswith('.py')]
EXECUTIONS_DIR = os.path.join(REPO_DIR, 'executions')

def timestamp():
    return datetime.now().astimezone().isoformat(' ', 'seconds')

def tprint(*args, **kwargs):
    print(timestamp(), *args, **kwargs)

def run(execution, kind):
    execution = os.path.join(EXECUTIONS_DIR, execution)
    with open(execution) as f:
        args = f.read().split()
    if args[0] in COMMANDS:
        p = subprocess.Popen(['python3', *args], cwd=COMMANDS_DIR)
        tprint(f'PID {p.pid} - start {kind} command `{args[0]}`')
        code = p.wait()
        tprint(f'PID {p.pid} - exited with code {code}')
    os.remove(execution)

while True:
    time.sleep(10)
    for execution in os.listdir(EXECUTIONS_DIR):
        if not execution.startswith('execution_'):
            continue
        kind = 'execution'
        if execution.startswith('execution_upkeep_'):
            try:
                t = int(execution.split('_')[2])
            except:
                t = 0
            if time.time() < t:
                continue
            kind = 'upkeep'
        run(execution, kind)
