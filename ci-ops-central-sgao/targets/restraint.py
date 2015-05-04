import uuid
import os
import sys
import logging

LOG = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NEEDED_PATHS = ['../tasks', '../lib', '../config', '../project']
NEEDED_PATHS = [os.path.join(THIS_DIR, p) for p in NEEDED_PATHS]
sys.path.extend(NEEDED_PATHS)

from tasks.restraint_task import RestraintTask

WORKSPACE = os.environ.get('WORKSPACE', THIS_DIR + '/../../')
RESOURCES_OUTPUT = os.environ.get('RESOURCES_OUTPUT',
                                  os.path.join(WORKSPACE, 'RESOURCES.txt'))

RESTRAINTREPO = \
    os.environ.get('RESTRAINTREPO',
                   'http://bpeck.fedorapeople.org/restraint/el6.repo')
USERS = os.environ.get('USERS', 'root,test')
u = str(uuid.uuid1())
HOSTSFILE = os.environ.get('HOSTSFILE', WORKSPACE + '/hosts-%s' % u)
SSH_KEYFILE = os.environ.get('SSH_KEYFILE', '')
REMOTE_USER = os.environ.get('REMOTE_USER', 'root')
JOBXML = os.environ.get('JOBXML', '')
USEIPS = os.environ.get('USEIPS', True)
USEIPS = USEIPS in ['true', 'True', True]
RUNLOCAL = os.environ.get('RUNLOCAL', True)
RUNLOCAL = RUNLOCAL in ['true', 'True', True]
PATTERN = os.environ.get('PATTERN', 'testsystems')

restraint_pipeline = {
    'task': RestraintTask,
    'resources_file': RESOURCES_OUTPUT,
    'restraint_repo': RESTRAINTREPO,
    'name': 'Restraint',
    'users': USERS,
    'hostsfile': HOSTSFILE,
    'private_key_file': SSH_KEYFILE,
    'remote_user': REMOTE_USER,
    'jobxml': JOBXML,
    'pattern': PATTERN,
    'useips': USEIPS,
    'runlocal': RUNLOCAL,
}

LOG.info("Running Restraint")
pipeline = [restraint_pipeline]
