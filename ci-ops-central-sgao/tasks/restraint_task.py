import taskrunner
import os
import logging
import time
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NEEDED_PATHS = ['../lib/ansiblehelpers']
NEEDED_PATHS = [os.path.join(THIS_DIR, p) for p in NEEDED_PATHS]
sys.path.extend(NEEDED_PATHS)

os.environ['ANSIBLE_HOST_KEY_CHECKING'] = 'False'

LOG = logging.getLogger(__name__)

from ansiblehelper import (
    ansible_call_local,
    ansible_call,
    log_ansible_call,
    add_ansible_hosts,
    fqdn_ip
)


class RestraintTask(taskrunner.Task):

    def __init__(self, resources_file, restraint_repo, name, users, jobxml,
                 hostsfile, private_key_file, remote_user='root',
                 pattern='testsystems', useips=True, runlocal=True, **kwargs):
        super(RestraintTask, self).__init__(**kwargs)

        self.resources_file = resources_file
        self.restraint_repo = restraint_repo
        self.name = name
        self.users = users
        self.jobxml = jobxml
        self.hostsfile = hostsfile
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.pattern = pattern
        self.useips = useips
        self.runlocal = runlocal
        self.msg = "Running Restraint test harness"
        self.clean_msg = "Cleaning up Restraint test harness"

    def run(self, context):

        if self.jobxml == '':
            raise ValueError("JOBXML is empty")

        LOG.info('%s:' % self.msg)
        LOG.info('\t%s' % self.name)
        LOG.info("Configuration:\n"
                 "resources_file:\t\t%s\n"
                 "users:\t\t\t%s\n"
                 "hostsfile:\t\t%s\n"
                 "private_key_file:\t%s\n"
                 "remote_user:\t\t%s\n"
                 "pattern:\t\t%s\n"
                 "useips:\t\t\t%s\n"
                 % (self.resources_file,
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

        # read resources.txt file
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
            driverlist = [{'ip': test_slaveip, 'name': test_slavename}]
        else:
            driverlist = []
        testresourcelist = []

        for resourcename in trlist:
            d = {}
            ip = fqdn_ip(resourcename)
            d['ip'] = ip
            d['name'] = resourcename
            testresourcelist.append(d.copy())
        LOG.info('--------------------------------------------------')

        LOG.info('Slave Driver: %s' % driverlist)
        LOG.info('Test Resources: %s' % testresourcelist)
        LOG.info('--------------------------------------------------')

        # Setup ansible host file defining the slave and test resource ip/names
        '''
            ansible host file
            [local]
            localhost     ansible_connection=local

            [slaves]
            10.8.49.184     ansible_connection=local

            [testsystems]
            rizzo.dqe.lab.eng.bos.redhat.com
        '''
        LOG.info("RESTRAINT: Creating ansible host file")
        add_ansible_hosts(self.hostsfile, self.private_key_file,
                          self.useips, self.runlocal, driverlist,
                          testresourcelist)

        LOG.info("Successfully created ansible host file")
        LOG.info('--------------------------------------------------')

        # install restraint repo
        LOG.info('install restraint repo')
        cmd = "wget -O /etc/yum.repos.d/restraint.repo %s" \
              % self.restraint_repo
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Set repo', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
            raise Exception('Error: install restraint repo')
        LOG.info("Install restraint repo - Successful")
        LOG.info('--------------------------------------------------')

        # yum -y remove beah
        LOG.info('yum -y remove beah')
        cmd = "yum -y remove beah"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Remove beah', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("yum -y remove beah - Successful")
        LOG.info('--------------------------------------------------')

        # yum -y remove rhts-test-env conflicts with restraintd rhts
        LOG.info('yum -y remove rhts-test-env')
        cmd = "yum -y remove rhts-test-env"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Remove rhts-test-env', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("yum -y remove rhts-test-env - Successful")
        LOG.info('--------------------------------------------------')

        # yum -y remove rhts-python conflicts with restraintd rhts
        LOG.info('yum -y remove rhts-python')
        cmd = "yum -y remove rhts-python"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Remove rhts-python', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("yum -y remove rhts-python - Successful")
        LOG.info('--------------------------------------------------')

        # install yum restraintd
        LOG.info('install -y yum restraintd')
        cmd = "yum -y install restraint"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Install Restraint', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("install -y yum restraintd - Successful")
        LOG.info('--------------------------------------------------')

        # install yum restraintd rhts beakerlib-redhat staf
        LOG.info('install -y yum gcc restraint-rhts beakerlib-redhat staf')
        cmd = "yum -y install restraint-rhts staf"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Set Repo', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("yum -y install restraint-rhts - Successful")
        LOG.info('--------------------------------------------------')

        # get beakerlib rpm
        LOG.info('get beakerlib rpm')
        cmd = "curl -k -o /root/beakerlib-1.9-3.el7.noarch.rpm " \
              "https://beaker.engineering.redhat.com/harness/" \
              "RedHatEnterpriseLinux7/beakerlib-1.9-3.el7.noarch.rpm"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Set Repo', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("get beakerlib rpm - Successful")
        LOG.info('--------------------------------------------------')

        # install beakerlib
        LOG.info('install rpm beakerlib')
        cmd = "yum localinstall -y /root/beakerlib-1.9-3.el7.noarch.rpm"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Set Repo', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("install rpm beakerlib - Successful")
        LOG.info('--------------------------------------------------')

        # get beakerlib-redhat rpm
        LOG.info('get beakerlib-redhat rpm')
        cmd = "curl -k -o /root/beakerlib-redhat-1-15.el7.noarch.rpm " \
              "https://beaker.engineering.redhat.com/harness/" \
              "RedHatEnterpriseLinux7/beakerlib-redhat-1-15.el7.noarch.rpm"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Set Repo', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("get beakerlib-redhat rpm - Successful")
        LOG.info('--------------------------------------------------')

        # install beakerlib-redhat
        LOG.info('install rpm beakerlib-redhat')
        cmd = "yum localinstall -y /root/beakerlib-redhat-1-15.el7.noarch.rpm"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Set Repo', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("install rpm beakerlib-redhat - Successful")
        LOG.info('--------------------------------------------------')

        # install beaker-tasks repo
        LOG.info('install beaker-tasks repo')
        cmd = "printf '[beaker-tasks]\nname=beaker-tasks\n" \
              "baseurl=http://beaker.engineering.redhat.com/rpms\n" \
              "enabled=1\ngpgcheck=0\n' > /etc/yum.repos.d/beaker-tasks.repo"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Set Repo', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("install beaker-tasks repo - Successful")
        LOG.info('--------------------------------------------------')

        # install restraint plugin to clean yum cache
        LOG.info('install restraint plugin to clean yum cache')
        cmd = "printf '#!/bin/sh -x\nyum clean all metadata\n'" \
              "> /usr/share/restraint/plugins/completed.d/70_clear_yum_cache;" \
              "chmod a+x " \
              "/usr/share/restraint/plugins/completed.d/70_clear_yum_cache"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Set Repo', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("install restraint plugin to clean yum cache "
                 "- Successful")
        LOG.info('--------------------------------------------------')

        # Enable the service for next reboot
        LOG.info('Enable the service for next reboot')
        cmd = "chkconfig --level 345 restraintd on"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('chkconfig ', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("chkconfig --level 345 restraintd on - Successful")
        LOG.info('--------------------------------------------------')

        # Start the service now
        LOG.info('Start the service now')
        cmd = "service restraintd start"
        LOG.info('Command: %s' % cmd)
        results = ansible_call('Start restraintd service', 'shell', cmd,
                               self.private_key_file, self.pattern,
                               self.remote_user, 10, self.hostsfile)

        if results['failures']:
            log_ansible_call(results)
        LOG.info("service restraintd start - Successful")
        LOG.info('--------------------------------------------------')

        # little delay
        time.sleep(60)

        # Running restraint xml now
        for target in testresourcelist:
            targethost = target['ip']
            LOG.info('Running Restraint XML now...%s ' % targethost)

            xml = self.jobxml
            cmd = "/usr/bin/restraint --verbose --host 1=%s --job %s" \
                  % (targethost, xml)
            LOG.info('Command: %s' % cmd)
            rc, xstdout, xstderr = ansible_call_local('Run restraint',
                                                      'shell', cmd,
                                                      'localhost', 'root',
                                                      10, self.hostsfile)
            LOG.info("ReturnCode:: %d" % rc)

            LOG.info("Stdout:")
            for line in xstdout.splitlines():
                LOG.info(line)

            LOG.info("Stderr:")
            errflag = False
            for line in xstderr.splitlines():
                LOG.info(line)
                errflag = True
            LOG.info('--------------------------------------------------')

            if errflag or rc > 0:
                LOG.info('***********************************************')
                raise Exception("Failed: %s" % cmd)
        LOG.info('Complete...')

    def cleanup(self, context):
        if os.path.exists(self.hostsfile) is True:
            LOG.info('Removing file %s' % self.hostsfile)
            os.remove(self.hostsfile)
        LOG.info(self.clean_msg)
