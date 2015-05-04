import os
import sys
import logging
from tasks.stack_janitor_task import StackJanitor
from targets import common

LOG = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NEEDED_PATHS = ['../tasks', '../lib', '../config', '../project']
NEEDED_PATHS = [os.path.join(THIS_DIR, p) for p in NEEDED_PATHS]
sys.path.extend(NEEDED_PATHS)

REMOVE_VMS = os.environ.get('REMOVE_VMS', 'True')
REMOVE_IPS = os.environ.get('REMOVE_IPS', 'True')


from provision_parser import (
    get_json_props,
    create_global_defaults,
    merge_all_props
)


def _get_fetcher(resource):
    """
    Return a function that allows out to get a specific property, first from
    the os.environment, then from the given resource, and at if not there
    return the default passed.
    """
    def _get_prop(pname, ename=None, default=None):
        if pname == 'name':
            pname = 'LABEL'
        if ename is None:
            ename = pname.upper()
        return os.environ.get(pname.upper(), resource.get(pname, default))
    return _get_prop

GLOBAL_DEFAULTS = \
    (os.environ.get('GLOBAL_DEFAULTS', THIS_DIR +
                    '/../jobs/global_defaults.json'))
PROJECT_DEFAULTS = \
    (os.environ.get('PROJECT_DEFAULTS', THIS_DIR +
                    '/../project/config/project_defaults.json'))

CLEANUP_DAYS = os.environ.get('CLEANUP_DAYS', '1')
CLEANUP_IGNORE_PATTERN = os.environ.get('CLEANUP_IGNORE_PATTERN',
                                        '.*permanent.*')
FLOATING_IP_DELAY = os.environ.get('FLOATING_IP_DELAY', '180')
FLOATING_IP_CHECKS = os.environ.get('FLOATING_IP_CHECKS', '3')

# TODO: Take into account other sites and add options in the config props

global_data = get_json_props(GLOBAL_DEFAULTS)
global_defaults = create_global_defaults(global_data)
project_data = get_json_props(PROJECT_DEFAULTS)
top_data = {}
final_props = merge_all_props([global_defaults, project_data, top_data])
for idx, resource in enumerate(final_props['resources']):
    _get_prop = _get_fetcher(final_props['sites'][0])
    SITE = _get_prop('site', default=None)
    # Openstack site properties
    ENDPOINT = _get_prop('endpoint', default=None)
    PROJECT = _get_prop('project', default=None)
    USERNAME = _get_prop('username', default=None)
    PASSWORD = _get_prop('password', default=None)


cleanup = [{
    'task': StackJanitor,
    'endpoint': ENDPOINT,
    'project': PROJECT,
    'username': USERNAME,
    'password': PASSWORD,
    'older_in_days': CLEANUP_DAYS,
    'ignore_pattern': CLEANUP_IGNORE_PATTERN,
    # wait flip_delay seconds between flip_count checks,
    # to be sure FloatingIP is not waiting
    # for some building/deleting VM/Job
    'flip_delay': FLOATING_IP_DELAY,
    'flip_count': FLOATING_IP_CHECKS,
    'remove_vms': REMOVE_VMS,
    'remove_ips': REMOVE_IPS
}]

if common.SITE == 'dev':
    cleanup[0]['older_in_days'] = 3

cleanup_test = [cleanup[0].copy()]
cleanup_test[0]['pretend'] = True
