import taskrunner
import os
import logging
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NEEDED_PATHS = ['../lib/ansiblehelpers']
NEEDED_PATHS = [os.path.join(THIS_DIR, p) for p in NEEDED_PATHS]
sys.path.extend(NEEDED_PATHS)

os.environ['ANSIBLE_HOST_KEY_CHECKING'] = 'False'

LOG = logging.getLogger(__name__)

from ansiblehelper import (
    ansible_sec_updates,
    ansible_playbook_call,
    log_ansible_call,
    add_ansible_hosts,
    fqdn_ip
)


class AnsibleTask(taskrunner.Task):

    def __init__(self, resources_file, playbooks, name, users, hostsfile,
                 private_key_file, remote_user='root',
                 pattern='testsystems', useips=True, runlocal=False, **kwargs):
        super(AnsibleTask, self).__init__(**kwargs)

        self.resources_file = resources_file
        self.playbooks = playbooks
        self.name = name
        self.users = users
        self.hostsfile = hostsfile
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.pattern = pattern
        self.useips = useips
        self.runlocal = runlocal

    def run(self, context):

        LOG.info('\t%s' % self.name)
        LOG.info("\n\nConfiguration:\n"
                 "resources_file:\t\t%s\n"
                 "playbooks:\t\t%s\n"
                 "users:\t\t\t%s\n"
                 "hostsfile:\t\t%s\n"
                 "private_key_file:\t%s\n"
                 "remote_user:\t\t%s\n"
                 "pattern:\t\t%s\n"
                 "useips:\t\t\t%s\n"
                 % (self.resources_file, self.playbooks,
                    self.users, self.hostsfile,
                    self.private_key_file, self.remote_user, self.pattern,
                    str(self.useips)))

        # driverlist = [{'ip':'10.18.41.220', 'name':'10.18.41.220'}]
        # testresourcelist = [{'ip':'10.16.134.92',
        #                      'name':'rizzo.dqe.lab.eng.bos.redhat.com'}]

        '''
            RESOURCES.txt
            BKR_JOBID=J:647672
            EXISTING_NODES=rizzo.dqe.lab.eng.bos.redhat.com
            SITE=qeos
            LABEL=kernel-5bd080ac-d2d2-4403-9609-8e99bbb4b1a9
            JSLAVEIP=10.8.49.184
            JSLAVENAME=pit-slave-rhel-6.5-x86-64_rev2
            JSLAVELABEL=pit-slave-rhel-6.5-x86-64_rev2
        '''
        LOG.info('Current Working Directory: %s' % os.getcwd())
        LOG.info('Current Jenkins Workspace: [%s]',
                 os.environ.get('WORKSPACE'))

        # read resources file
        LOG.info('Resource File: [%s]' % self.resources_file)

        # objects to setup to create ansible files
        resourcesdict = {}
        env_vars = []

        # test to see if the RESOURCE.txt file exists
        if os.path.isfile(self.resources_file):
            LOG.info('Reading the resources file: %s' % self.resources_file)

            with open(self.resources_file, 'r') as env_file:
                for line in env_file:
                    env_vars.append(line[:-1])

            for item in env_vars:
                    k, v = item.split('=')
                    if 'EXISTING_NODES' in k:
                        resourcesdict['EXISTING_NODES'] = \
                            os.environ.get('EXISTING_NODES', v)
                    if 'LABEL' in k:
                        resourcesdict['LABEL'] = os.environ.get('LABEL', v)
                    if 'JSLAVENAME' in k \
                            or os.environ.get('JSLAVENAME') is not None:
                        resourcesdict['JSLAVENAME'] = \
                            os.environ.get('JSLAVENAME', v)
                    elif os.environ.get('JSLAVENAME') == '' \
                            or os.environ.get('JSLAVENAME') is None:
                        resourcesdict['JSLAVENAME'] = ''
                    if 'JSLAVELABEL' in k \
                            or os.environ.get('JSLAVELABEL') is not None:
                        resourcesdict['JSLAVELABEL'] = \
                            os.environ.get('JSLAVELABEL', v)
                    elif os.environ.get('JSLAVELABEL') == '' \
                            or os.environ.get('JSLAVELABEL') is None:
                        resourcesdict['JSLAVELABEL'] = ''
                    if 'JSLAVEIP' in k \
                            or os.environ.get('JSLAVEIP') is not None:
                        resourcesdict['JSLAVEIP'] = \
                            os.environ.get('JSLAVEIP', v)
                    elif os.environ.get('JSLAVEIP') == '' \
                            or os.environ.get('JSLAVEIP') is None:
                        resourcesdict['JSLAVEIP'] = ''

            test_slavename = resourcesdict['JSLAVENAME']
            test_slaveip = resourcesdict['JSLAVEIP']
            test_testreourceips = resourcesdict['EXISTING_NODES']

            # convert hostname/ips to a list of hostname/ips
            trlist = test_testreourceips.split(',')
            LOG.info('Resource file ip list: %s' % str(trlist))

        else:
            LOG.error('Resource file does not exist so exiting, '
                      '[RESOURCE.txt]...')
            raise Exception("Resource file does not exist so exiting, "
                            "[RESOURCE.txt]...")

        if test_slaveip != '' and test_slavename != '':
            jslavelist = [{'ip': test_slaveip, 'name': test_slavename}]
        else:
            jslavelist = []
        testresourcelist = []

        for resourcename in trlist:
            d = {}
            ip = fqdn_ip(resourcename)
            d['ip'] = ip
            d['name'] = resourcename
            testresourcelist.append(d.copy())
        LOG.info('--------------------------------------------------')

        LOG.info('Jenkins Slave: %s' % jslavelist)
        LOG.info('Test Resources: %s' % testresourcelist)
        LOG.info('--------------------------------------------------')

        # Setup ansible host file defining the slave and test resource ip/names
        '''
            ansible host file
            [local]
            localhost     ansible_connection=local

            [slaves]
            10.8.49.184

            [testsystems]
            rizzo.dqe.lab.eng.bos.redhat.com
        '''
        LOG.info("Creating ansible host file")
        add_ansible_hosts(self.hostsfile, self.useips, self.runlocal,
                          jslavelist, testresourcelist, self.pattern)

        LOG.info("Successfully created ansible host file")
        LOG.info('--------------------------------------------------')

        LOG.info("Set security config for Ansible")
        ansible_sec_updates(self.private_key_file, self.hostsfile)
        LOG.info('--------------------------------------------------')

        LOG.info("Execute playbooks:\n%s" % self.playbooks)

        for playbook in self.playbooks:
            playbook = os.environ.get('WORKSPACE') + '/' + (playbook)
            results = ansible_playbook_call('ci-ansible-playbook-exec',
                                            playbook, self.private_key_file,
                                            self.hostsfile, self.remote_user,
                                            {'hosts': self.pattern})
            if results['failures']:
                log_ansible_call(results)

            if results['failures'] == 0:
                LOG.info("Execution of ansible playbook %s - Successful"
                         % playbook)
            else:
                LOG.info("Execution of ansible playbook %s - Failed"
                         % playbook)

        LOG.info('--------------------------------------------------')

    def cleanup(self, context):
        if os.path.exists(self.hostsfile) is True:
            LOG.info('Removing file %s' % self.hostsfile)
            os.remove(self.hostsfile)
        LOG.info("Cleanup after ansible execution")
