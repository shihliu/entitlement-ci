import os
import sys
import logging
import uuid

LOG = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NEEDED_PATHS = ['../tasks', '../lib', '../config', '../project']
NEEDED_PATHS = [os.path.join(THIS_DIR, p) for p in NEEDED_PATHS]
sys.path.extend(NEEDED_PATHS)

from tasks.get_nodes_task import GetNodes, MockGetNodes
from tasks.get_bkrnodes_task import GetBkrNodes
from provision_parser import (
    get_json_props,
    create_global_defaults,
    merge_all_props
)
from tasks.foremanfactory import GetForemanNodesTask
from tasks.extract_resources_task import ExtractResources
from tasks.run_command_task import RunCommand
from tasks.ansible_task import AnsibleTask
from tasks.repo_create_task import RepoCreate
from tasks.install_packages_task import InstallPkgs


def _get_fetcher(resource):
    """
    Return a function that allows out to get a specific property, first from
    the os.environment, then from the given resource, and at if not there
    return the default passed.
    """
    def _get_prop(pname, ename=None, default=None):
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
TOPOLOGY = \
    (os.environ.get('TOPOLOGY',
                    THIS_DIR + '/../project/config/aio_jslave.json'))

BEAKER_CONF = \
    (os.environ.get('BEAKER_CONF', '/etc/beaker/client.conf'))

WORKSPACE = os.environ.get('WORKSPACE', THIS_DIR + '/../..')
RESOURCES_OUTPUT = os.environ.get('RESOURCES_OUTPUT', THIS_DIR
                                  + '/../../RESOURCES.txt')
ANSIBLE_INVENTORY = os.environ.get('ANSIBLE_INVENTORY', THIS_DIR
                                   + '/../../ansible_inventory.txt')
resources_files = []
pipeline = []
ansible_pipeline = []

# Cleanup resources - first in the pipeline
cleanup_resources_output = {
    'task': RunCommand,
    'command': ('rm -f %s' % RESOURCES_OUTPUT),
    'remote': False,
}
pipeline.append(cleanup_resources_output)

# Cleanup ansible inventory - first in the pipeline
cleanup_ansible_inventory = {
    'task': RunCommand,
    'command': ('rm -f %s' % ANSIBLE_INVENTORY),
    'remote': False,
}
pipeline.append(cleanup_ansible_inventory)


# TODO: Take into account other sites and add options in the config props

global_data = get_json_props(GLOBAL_DEFAULTS)
global_defaults = create_global_defaults(global_data)
project_data = get_json_props(PROJECT_DEFAULTS)
top_data = get_json_props(TOPOLOGY)
final_props = merge_all_props([global_defaults, project_data, top_data])
for idx, resource in enumerate(final_props['resources']):
    _get_prop = _get_fetcher(final_props['sites'][0])
    SITE = _get_prop('site', default=None)
    # Openstack site properties
    ENDPOINT = _get_prop('endpoint', default=None)
    PROJECT = _get_prop('project', default=None)
    USERNAME = _get_prop('username', default=None)
    PASSWORD = _get_prop('password', default=None)
    KEYPAIR = _get_prop('keypair', default=None)
    NETWORKS = _get_prop('networks', default=None)
    REGION = _get_prop('region', default=None)

    # Foreman site properties
    FOREMAN_URL = _get_prop('foreman_url', default=None)
    FOREMAN_USERNAME = _get_prop('foreman_username', default=None)
    FOREMAN_PASSWORD = _get_prop('foreman_password', default=None)
    FOREMAN_VERSION = _get_prop('foreman_version', default='1.5.0')
    OS_MAPPING_FOREMAN = _get_prop('os_mapping_foreman', default={'Redhat-6':
                                   dict(ptable='Kickstart default',
                                        media='RHEL 6.5')})

    # Satellite site properties
    SATELLITE_URL = _get_prop('satellite_url', default=None)
    SATELLITE_USERNAME = _get_prop('satellite_username', default=None)
    SATELLITE_PASSWORD = _get_prop('satellite_password', default=None)
    SATELLITE_VERSION = _get_prop('satellite_version', default='6.0.1')
    OS_MAPPING_SATELLITE = _get_prop(
        'content_view_mapping_satellite',
        default={
            'RHEL6_Server_Content_View': {
                'RHEL6-Server-Content-View': dict(
                    ptable='Kickstart default',
                    media='Red_Hat_6_Server_Kickstart_x86_64_6Server')
            }
        }
    )

    _get_prop = _get_fetcher(resource)
    # Openstack resource properties
    FLAVOR = _get_prop('flavor', default='')
    IMAGE = _get_prop('image', default='')
    LABEL = os.environ.get("LABEL", _get_prop('name', default='ci-ops'))
    UUID = os.environ.get("UUID", None)
    USERDATAFILES = _get_prop('user-data-files', default=[])
    COUNT = _get_prop('count', default=1)

    # Beaker resource properties
    JOB_GROUP = _get_prop('job_group', default='')
    RETENTION_TAG = _get_prop('retention_tag', default='Scratch')
    RANDOM = _get_prop('random', default=False)
    RANDOM = RANDOM in ['true', 'True', True]
    RECIPESETS = _get_prop('recipesets', default=[])
    METADATA = _get_prop('metadata', default=None)
    JOB_NAME = _get_prop('job_name', default='Not started by Jenkins')
    BUILD_NUMBER = _get_prop('build_number', default='')
    SKIP_MAX_ATTEMPTS = _get_prop('skip_max_attempts', default=False)
    SKIP_MAX_ATTEMPTS = SKIP_MAX_ATTEMPTS in ['true', 'True', True]
    SKIP_NO_SYSTEM = _get_prop('skip_no_system', default=False)
    SKIP_NO_SYSTEM = SKIP_NO_SYSTEM in ['true', 'True', True]
    SKIP_UUID = _get_prop('skip_uuid', default=False)
    SKIP_UUID = SKIP_UUID in ['true', 'True', True]

    # Jenkins defines env variables JOB_NAME and BUIld_NUMBER that we
    # add to the Beaker Whiteboard description
    if BUILD_NUMBER != '':
        JOB_NAME = 'Jenkins Job Name: ' + JOB_NAME
        BUILD_NUMBER = 'Jenkins Build #: ' + BUILD_NUMBER

    # Foreman/Satellite resource properties
    HOSTGROUP = _get_prop('hostgroup', default='')
    HOSTNAMES = _get_prop('hostnames', default=[])
    PREFIX = _get_prop('prefix', default='')
    SSH_USER = _get_prop('ssh_user', default='root')
    SSH_PASS = _get_prop('ssh_pass', default='qum5net')
    LOCATION = _get_prop('location', default='')
    ORGANIZATION = _get_prop('organization', default='')
    LIFECYCLE = _get_prop('lifecycle', default='')
    REBUILD = _get_prop('rebuild', default=True)
    REBUILD = REBUILD in ['true', 'True', True]
    RESERVE = _get_prop('reserve', default=False)
    RESERVE = RESERVE in ['true', 'True', True]

    # Openstack, Foreman, Beaker
    SSH_KEYFILE = _get_prop('ssh_keyfile')

    # Used to execute ci-provisioner playbooks as well as ones provided
    # by users
    ANSIBLE = _get_prop('ansible', default={})

    REPOS = _get_prop('repos', default=[])
    PACKAGES = _get_prop('packages', default=[])

    if UUID != '' and UUID is not None:
        LABEL = LABEL + '-' + UUID

    if len(final_props['resources']) > 1:
        LABEL = LABEL + '-rs-' + str(idx+1)

    RESOURCES_FILE = os.environ.get('RESOURCES_FILE', '../' + LABEL + '.json')
    resources_files.append(RESOURCES_FILE)
    resources_json = open(RESOURCES_FILE, 'w')

    # Add create_bkr_nodes to pipeline if JOB_GROUP and ARCHES not empty
    if JOB_GROUP != "" and RECIPESETS != "":
        # Provision resources in Beaker
        create_bkr_nodes = {
            'task': GetBkrNodes,
            'count': int(COUNT),
            'job_group': JOB_GROUP,
            'recipesets': RECIPESETS,
            'debug': True,
            'dryrun': False,
            'prettyxml': True,
            'whiteboard': JOB_GROUP
            + ' resources '
            + JOB_NAME + ' '
            + BUILD_NUMBER,
            'retention_tag': RETENTION_TAG,
            'random': RANDOM,
            'metadata': METADATA,
            'skip_max_attempts': SKIP_MAX_ATTEMPTS,
            'skip_no_system': SKIP_NO_SYSTEM,
            'resources_file': RESOURCES_FILE,
        }
        LOG.info("Provisioning in Beaker since JOB_GROUP "
                 "and RECIPESETS are defined")
        pipeline.append(create_bkr_nodes)

    # Add create_nodes to pipeline if FLAVOR and IMAGE not empty
    if FLAVOR != "" and IMAGE != "":
        # Provision resources in Openstack
        create_nodes = {
            'task': GetNodes,
            'count': int(COUNT),
            'node_name': LABEL,
            'endpoint': ENDPOINT,
            'project': PROJECT,
            'username': USERNAME,
            'password': PASSWORD,
            'keypair': KEYPAIR,
            'ssh_keyfile': SSH_KEYFILE,
            'image': IMAGE,
            'flavor': FLAVOR,
            'rhn_deregister': True,
            'networks': NETWORKS,
            'metadata': METADATA,
            'resources_file': RESOURCES_FILE,
            'user_data_files': USERDATAFILES,
        }
        LOG.info("Provisioning in Cloud-Openstack since "
                 "FLAVOR and IMAGE are defined")
        pipeline.append(create_nodes)

    if HOSTGROUP != "" or PREFIX != "" or HOSTNAMES != []:
        if 'name' in resource and resource['name'] in ['foreman', 'satellite']:
            IS_SATELLITE = (resource['name'] == 'satellite')
        else:
            raise Exception('"name" attribute is missing or it is not'
                            ' set to "foreman" or "satellite"')
        if IS_SATELLITE and '' in [LOCATION, ORGANIZATION, LIFECYCLE]:
            # TODO(bshuster): mention the missing fields in the exception
            raise Exception('`location`, `organization` and `lifecycle` are '
                            'required when reprovision in Satellite')

        PROVISION_TOOL_URL = SATELLITE_URL if IS_SATELLITE else FOREMAN_URL
        PROVISION_TOOL_USERNAME = SATELLITE_USERNAME if IS_SATELLITE\
            else FOREMAN_USERNAME
        PROVISION_TOOL_PASSWORD = SATELLITE_PASSWORD if IS_SATELLITE\
            else FOREMAN_PASSWORD
        PROVISION_TOOL_VERSION = SATELLITE_VERSION if IS_SATELLITE\
            else FOREMAN_VERSION
        PROVISION_TOOL_OS_MAPPING = OS_MAPPING_SATELLITE if IS_SATELLITE\
            else OS_MAPPING_FOREMAN
        PROVISION_TOOL_NAME = 'Satellite' if IS_SATELLITE else 'Foreman'

        # Provision resources in Foreman/Satellite
        create_foreman_nodes = {
            'name': PROVISION_TOOL_NAME,
            'task': GetForemanNodesTask,
            'foreman_url': PROVISION_TOOL_URL,
            'username': PROVISION_TOOL_USERNAME,
            'password': PROVISION_TOOL_PASSWORD,
            'foreman_version': PROVISION_TOOL_VERSION,
            'rebuild': REBUILD,
            'existing_nodes': HOSTNAMES,
            'distribution': IMAGE,
            'reserve': RESERVE,
            'reserve_message': LABEL,
            'ssh_user': SSH_USER,
            'ssh_pass': SSH_PASS,
            'ssh_keyfile': None,
            'os_mapping': PROVISION_TOOL_OS_MAPPING,
            'count': COUNT,
            'is_satellite': IS_SATELLITE,
            'organization': ORGANIZATION,
            'location': LOCATION,
            'lifecycle': LIFECYCLE,
        }
        LOG.info("Provisioning in %s since HOSTGROUP "
                 "or PREFIX or HOSTNAMES are defined" % PROVISION_TOOL_NAME)
        pipeline.append(create_foreman_nodes)

    # Add repos if defined
    if REPOS != []:
        for repo in REPOS:
            if 'enabled' in repo:
                R_ENABLED = int(repo['enabled'])
            else:
                R_ENABLED = 1
            if 'skip_if_unavailable' in repo:
                R_SKIP = int(repo['skip_if_unavailable'])
            else:
                R_SKIP = 0
            if 'gpgcheck' in repo:
                R_GPGCHECK = int(repo['gpgcheck'])
            else:
                R_GPGCHECK = 0
            if 'name' in repo:
                R_NAME = repo['name']
            else:
                if UUID is None:
                    R_NAME = 'provisioner_repo' + str(uuid.uuid1())
                else:
                    R_NAME = 'provisioner_repo' + UUID

            repo_creation = {
                'task': RepoCreate,
                'name': R_NAME,
                'enabled': R_ENABLED,
                'skip_if_unavailable': R_SKIP,
                'gpgcheck': R_GPGCHECK,
            }
            if 'baseurl' in repo:
                repo_creation.update({'baseurl': repo['baseurl']})
            if 'mirrorlist' in repo:
                repo_creation.update({'mirrorlist': repo['mirrorlist']})

            pipeline.append(repo_creation)
        LOG.info("Adding repos to deployed resources")

    # Install yum and/or pip packages
    if PACKAGES != []:
        for package in PACKAGES:
            if 'yum' in package:
                YUM_PKGS = package['yum']
            else:
                YUM_PKGS = None
            if 'pip' in package:
                PIP_PKGS = package['pip']
            else:
                PIP_PKGS = None

            install_pkgs = {
                'task': InstallPkgs,
                'yum_pkgs': YUM_PKGS,
                'pip_pkgs': PIP_PKGS
            }

            pipeline.append(install_pkgs)
        LOG.info("Adding packages to be installed on resources")

    # Execute Ansible playbooks if defined
    if ANSIBLE != {}:
        if 'playbooks' in ANSIBLE:
            ANSIBLEPLAYBOOKS = ANSIBLE['playbooks']
            if 'pattern' in ANSIBLE:
                PATTERN = ANSIBLE['pattern']
            else:
                PATTERN = 'testsystems'
            if 'remote_user' in ANSIBLE:
                REMOTE_USER = ANSIBLE['remote_user']
            else:
                REMOTE_USER = 'root'
            if 'users' in ANSIBLE:
                USERS = ANSIBLE['users']
            else:
                USERS = 'root,test'
            if 'useips' in ANSIBLE:
                USEIPS = ANSIBLE['useips']
                USEIPS = USEIPS in ['true', 'True', True]
            else:
                USEIPS = True
            if 'runlocal' in ANSIBLE:
                RUNLOCAL = ANSIBLE['runlocal']
                RUNLOCAL = RUNLOCAL in ['false', 'False', False]
            else:
                RUNLOCAL = False
            if UUID is None:
                HOSTSFILE = os.environ.get('HOSTSFILE',
                                           WORKSPACE +
                                           '/hosts-%s.txt' % str(uuid.uuid1()))
            else:
                HOSTSFILE = os.environ.get('HOSTSFILE',
                                           WORKSPACE + '/hosts-%s.txt' % UUID)
            ansible_execution = {
                'task': AnsibleTask,
                'resources_file': RESOURCES_OUTPUT,
                'playbooks': ANSIBLEPLAYBOOKS,
                'name': 'Provisioner and Ansible execution',
                'users': USERS,
                'hostsfile': HOSTSFILE,
                'private_key_file': SSH_KEYFILE,
                'pattern': PATTERN,
                'remote_user': REMOTE_USER,
                'useips': USEIPS,
                'runlocal': RUNLOCAL
            }
            LOG.info("Adding ansible playbook execution "
                     "since playbooks are defined")
            ansible_pipeline.append(ansible_execution)

# Collect resources - end of the pipeline
extract_resources = {
    'task': ExtractResources,
    'resources_files': resources_files,
    'resources_output': RESOURCES_OUTPUT,
    'ansible_inventory': ANSIBLE_INVENTORY,
}
pipeline.append(extract_resources)

mock_create_nodes = {
    'task': MockGetNodes,
    'existing_nodes': os.environ.get('EXISTING_NODES', '').split(','),
    'ssh_user': 'root',
    'ssh_pass': '123456',
    'ssh_keyfile': SSH_KEYFILE,
}

provision_pipeline = pipeline + ansible_pipeline
