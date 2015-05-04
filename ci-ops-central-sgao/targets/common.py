import os
import re

from tasks.get_nodes_task import GetNodes, MockGetNodes

# qeos, tlv, brq
SITE = os.environ.get('SITE', 'qeos')

# rhos-3.0, rdo-grizzly, rhos-4.0, rdo-havana
OS_VERSION = os.environ.get('OS_VERSION', 'rhos-4.0')

# rhel-6.4, rhel-6.5, fedora-19
DISTRIBUTION = os.environ.get('DISTRIBUTION', 'rhel-6.5')

# aio, 2comp
# see https://wiki.test.redhat.com/RhevmQe/OpenStackTeam/AutomatedJobNaming
TOPOLOGY = os.environ.get('TOPOLOGY', 'aio')

# novanetwork, neutron
NETWORKING = os.environ.get('NETWORKING', 'novanetwork')

# tempest-<branch>-<test_part>-<other_tags>, see tests.py
TESTS = os.environ.get('TESTS', 'tempest-havana-full')

GRIZZLY_PUDDLE = os.environ.get('GRIZZLY_PUDDLE', 'latest')
HAVANA_PUDDLE = os.environ.get('HAVANA_PUDDLE', 'latest')


def grizzly_subfolder(puddle):
    # Support for puddles in old non-errata format
    if not re.match('2013.*|2014-01.*', puddle):
        # Errata format
        return 'RHOS-3.0/'
    # old format
    return

WORKSPACE = os.environ.get('WORKSPACE', '.')

# used as a base name for the VMs, external storage and other resources
LABEL = os.environ.get('USER', 'user') + '_node'
if 'BUILD_TAG' in os.environ:
    LABEL = os.environ['BUILD_TAG']
elif 'JOB_NAME' in os.environ:
    LABEL = os.environ['JOB_NAME']

JENKINS_NAME = os.environ.get('JENKINS_NAME', '')
if JENKINS_NAME:
    LABEL = JENKINS_NAME + '-' + LABEL

get_nodes = {
    'task': GetNodes,
    'count': 1,
    'node_name': LABEL,
    'endpoint': 'http://qeos.lab.eng.rdu2.redhat.com:5000/v2.0/',
    'project': 'rhos-jenkins',
    'username': 'rhos-jenkins',
    'password': 'qum5net',
    'keypair': 'rhos-jenkins',
    'ssh_keyfile': './targets/keys/rhos-jenkins',
    'image': DISTRIBUTION + '_jeos',
    'flavor': 'm1.medlarge',
    'rhn_deregister': True,
    'networks': ['rhos-jenkins']
}

if 'parallel' in TESTS or 'upstream' in OS_VERSION:
    get_nodes['flavor'] = 'm1.large'

if 'fedora' in DISTRIBUTION:
    get_nodes['short_names'] = True

# use different credentials if not using the default location
if SITE == 'os1':
    get_nodes['endpoint'] = 'http://control.os1.phx2.redhat.com:5000/v2.0/'
    get_nodes['project'] = 'RHOS QE'
    get_nodes['password'] = '593970e0bf4d'
    get_nodes['networks'] = []
    get_nodes['explicit_floating_ips'] = False
    get_nodes['flavor'] = 'm1.large'
if SITE == 'tlv':
    get_nodes['endpoint'] = 'http://blue.rhos.qa.lab.tlv.redhat.com:5000/v2.0/'
    get_nodes['networks'] = ['int_net']
    get_nodes['flavor'] = 'm1.large'
elif SITE == 'brq':
    get_nodes['endpoint'] = ('http://controller.rhos.rhev.lab.eng.brq'
                             '.redhat.com:5000/v2.0/')
    get_nodes['networks'] = ['notrouted-shared']
    get_nodes['password'] = '123456'
    get_nodes['flavor'] = 'm1.medium'
elif SITE == 'afazekas':
    get_nodes['endpoint'] = 'http://192.168.84.100:5000/v2.0'
    get_nodes['networks'] = ['default']
    get_nodes['flavor'] = 'm1.large'

if TOPOLOGY == '2comp':
    get_nodes['count'] = 3


mock_get_nodes = {
    'task': MockGetNodes,
    'existing_nodes': os.environ.get('EXISTING_NODES', '').split(','),
    'ssh_user': 'root',
    'ssh_pass': '123456',
}
