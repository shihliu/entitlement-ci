import uuid
import os
import sys
import logging

LOG = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NEEDED_PATHS = ['../tasks', '../lib', '../config', '../project']
NEEDED_PATHS = [os.path.join(THIS_DIR, p) for p in NEEDED_PATHS]
sys.path.extend(NEEDED_PATHS)

from tasks.ansible_task import AnsibleTask

WORKSPACE = os.environ.get('WORKSPACE', THIS_DIR + '/../../')
RESOURCES_OUTPUT = os.environ.get('RESOURCES_OUTPUT',
                                  os.path.join(WORKSPACE, 'RESOURCES.txt'))

USERS = os.environ.get('USERS', 'root,test')
u = str(uuid.uuid1())
HOSTSFILE = os.environ.get('HOSTSFILE', WORKSPACE + '/hosts-%s' % u)
SSH_KEYFILE = os.environ.get('SSH_KEYFILE', '')
REMOTE_USER = os.environ.get('REMOTE_USER', 'root')
ANSIBLEPLAYBOOKS = os.environ.get('ANSIBLEPLAYBOOKS', '')
ANSIBLEPLAYBOOKS = ANSIBLEPLAYBOOKS.split(",")
NAME = os.environ.get('NAME', 'Ansible-Exec')
USEIPS = os.environ.get('USEIPS', True)
USEIPS = USEIPS in ['true', 'True', True]
RUNLOCAL = os.environ.get('RUNLOCAL', False)
RUNLOCAL = RUNLOCAL in ['false', 'False', False]
PATTERN = os.environ.get('PATTERN', 'testsystems')

ansible_pipeline = {
    'task': AnsibleTask,
    'resources_file': RESOURCES_OUTPUT,
    'playbooks': ANSIBLEPLAYBOOKS,
    'name': NAME,
    'users': USERS,
    'hostsfile': HOSTSFILE,
    'private_key_file': SSH_KEYFILE,
    'remote_user': REMOTE_USER,
    'pattern': PATTERN,
    'useips': USEIPS,
    'runlocal': RUNLOCAL
}

LOG.info("Running Ansible Playbooks")
pipeline = [ansible_pipeline]
