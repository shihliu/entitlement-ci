import logging
import taskrunner
import urlparse
from job_runner.utilities.machine import CommandExecutionError

from tasks import common

LOG = logging.getLogger(__name__)


class SetupJslave(taskrunner.Task):
    """
    Setup Jenkins slave, Install Java, download swarm, setup swarm connection.
    """
    deps = ['python-paramiko', 'java-1.7.0-openjdk', 'krb5-workstation', 'git',
            'wget', 'python-pip', 'python-unittest2',
            'python-pep8', 'python-flake8', 'python-futures']
    pip_deps = ['nose']

    def __init__(self, jslave_deps=None, jenkins_master_url=None,
                 jenkins_master_username=None,
                 jenkins_master_password=None,
                 jslave_name=None, jslave_label=None,
                 jswarm_url='http://repo.jenkins-ci.org/'
                            'releases/org/jenkins-ci/plugins/swarm-client',
                 jswarm_ver=None, jswarm_execs=None, jswarm_home=None,
                            ssh_keyfile=None,
                 jswarm_jar_loc='/root',
                 jslave_procs=['swarm'], skip_cust=False, **kwargs):
        """
        :param jslave_deps: list of yum packages needed by the jobs
        :param jenkins_master_url: Jenkins master url you want to connect to
        :param jenkins_master_username: Jenkins master username
        :param jenkins_master_password: Jenkins master password
        :param jslave_name: Jenkins slave name used for when connecting
        :param jslave_label: Jenkins slave label used for when connecting
        :param jswarm_url: Base location of the jswarm plugin
        :param jswarm_ver: Version of the swarm plugin
        :param jswarm_execs: Number of executors to utilize on the slave
        :param jswarm_home: Directory where Jenkins places files
        :param ssh_keyfile: path to the file with the private key of `keypair`
        :param jswarm_jar_loc: Location of the swarm jar file
        :param jslave_procs: name of jslave processes default is swarm only
        :param skip_cust: skip setting up kerb and keytabs from the master
        """
        super(SetupJslave, self).__init__(**kwargs)
        self.jslave_deps = jslave_deps or []
        self.jenkins_url = jenkins_master_url
        self.jenkins_user = jenkins_master_username
        self.jenkins_password = jenkins_master_password
        self.jslave_name = jslave_name
        self.jslave_label = jslave_label
        self.jswarm_url = jswarm_url
        self.jswarm_ver = jswarm_ver
        self.jswarm_execs = jswarm_execs
        self.jswarm_home = jswarm_home
        self.ssh_keyfile = ssh_keyfile
        self.jswarm_jar_loc = jswarm_jar_loc
        self.jslave_procs = jslave_procs
        self.skip_cust = skip_cust
        self.jswarm_jar = self.jswarm_jar_loc + 'swarm-client-' \
                                              + self.jswarm_ver \
                                              + '-jar-with-dependencies.jar'

    def run(self, context):
        node = context['nodes'].nodes[0]
        ip = context['nodes'].floating_ips[0]

        common.install_packages(node, self.deps + self.jslave_deps,
                                self.pip_deps)

        self._add_certificate(node)
        self._add_ip_to_hosts(node, ip)
        self._upload_ssh_keys(node)
        self._setup_jenkins_user(node)
        if self._check_for_plugin(node):
            LOG.info("Swarm agent plugin is present")
            self._setup_jswarm_conn(node)
        else:
            self._download_swarm_agent(node)
            self._setup_jswarm_conn(node)
        if self.skip_cust is False:
            self._setup_kerberos(node)
            self._setup_keytab(node)

        LOG.info('Jenkins slave setup running from %s' % ip)

    def cleanup(self, context):
        pass

    def _check_for_plugin(self, node):
        """
            Check if swarm plugin is already present
        """
        cmd_out = node.cmd("ls %s | xargs -i echo {}" % self.jswarm_jar)
        if "No such file or directory" in cmd_out:
            return False
        else:
            return True

    def _add_certificate(self, node):
        """
            Add RedHat certificate
            In our corporate environment,
            we have to add the internal Red Hat CA
            cert to not run into SSL errors everywhere.
        """
        node.cmd('/usr/bin/wget -O newca.crt --no-check-certificate'
                 ' https://password.corp.redhat.com/newca.crt')
        node.cmd('cat newca.crt | /usr/bin/certutil -d sql:/etc/pki/nssdb'
                 ' -A -t "C,," -n RedHat_CA')
        # for java
        try:
            keytool_pass = 'changeit'
            node.cmd('echo "%s" | keytool -import -file newca.crt'
                     ' -alias RedHat_CA -keystore'
                     ' /usr/lib/jvm/jre/lib/security/cacerts'
                     ' -noprompt' % keytool_pass)
        except CommandExecutionError, ex:
            if 'already exists' not in ex.message:
                raise

    def _add_ip_to_hosts(self, node, node_ip):
        """
            Add ip to the hosts file
        """
        node.cmd('echo "%s `hostname`" >> /etc/hosts' % node_ip)

    def _upload_ssh_keys(self, node):
        """
            Upload a private key to the slave
        """

        with open(self.ssh_keyfile, 'r') as ssh_keyfile_content:
            ssh_private_key = ssh_keyfile_content.read()
        node.cmd('echo "%s" > ~/.ssh/id_rsa' % ssh_private_key)
        node.cmd('ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub')
        self._allow_unchecked_ssh(node)

    def _setup_jenkins_user(self, node):
        """
            Setup jenkins user
        """
        cmd_out = node.cmd("grep 'jenkins' /etc/passwd | xargs -i echo {}")
        if 'jenkins' not in cmd_out:
            node.cmd('useradd jenkins')
        node.cmd('echo "jenkins:jenkins" | chpasswd')
        node.cmd('echo "jenkins    ALL=(ALL)    NOPASSWD: ALL" '
                 '>> /etc/sudoers')

    def _allow_unchecked_ssh(self, node):
        """
            Allow ssh from node without server fprint/ip verification.
        """
        node.cmd('echo "Host *\n'
                 '    UserKnownHostsFile=/dev/null\n'
                 '    StrictHostKeyChecking=no\n'
                 '    CheckHostIP=no\n'
                 '" >> /etc/ssh/ssh_config')

    def _download_swarm_agent(self, node):
        """
            Download the Jenkins Swarm plugin on the slave
        """
        node.cmd(("/usr/bin/wget"
                  " -O swarm-client-'%s'-jar-with-dependencies.jar"
                  " '%s'/'%s'/swarm-client-'%s'-jar-with-dependencies.jar")
                 % (self.jswarm_ver, self.jswarm_url, self.jswarm_ver,
                    self.jswarm_ver))

    def _setup_jswarm_conn(self, node):
        """
            Setup the Jenkins Swarm plugin on the slave
        """
        command = ['/usr/bin/java', '-jar', self.jswarm_jar,
                   '-master', self.jenkins_url, '-name',
                   self.jslave_name, '-executors',
                   self.jswarm_execs, '-labels',
                   self.jslave_label, '-fsroot',
                   self.jswarm_home,
                   '-mode', 'exclusive',
                   '-disableSslVerification']
        if self.jenkins_user and self.jenkins_password:
            command.extend(['-username', self.jenkins_user,
                            '-password', self.jenkins_password])
        elif self.jenkins_user or self.jenkins_password:
            msg = 'Jenkins master username or password not specified.  ' \
                  'Attempting to connect without authentication.'
            LOG.warning(msg)
        (result, pid) = node.runCmd(command, bg=True)

        LOG.info('Result of Jenkins swarm plugin running is %s' % result)
        LOG.info('Jenkins swarm plugin pid is %s' % pid)

    def _setup_kerberos(self, node):
        """
            Download and setup the kerberos config file from the master
        """
        master_ip = self._get_master_ip()
        krb_config = "/etc/krb5.conf"

        """
        Copy kerberos file from master
        """
        LOG.info('Checking Jenkins master for Kerberos configuration file')
        if common.remote_file_exists(node, master_ip, krb_config):
            LOG.info('Kerberos configuration found on Jenkins master at %s'
                     % master_ip)
            """ Copy Kerberos config file from master to slave
            """
            LOG.info('Copying Kerberos configuration file from'
                     ' Jenkins master')
            node.cmd("scp %s:%s /etc" % (master_ip, krb_config), timeout=120,
                     cmd_list=False)
        else:
            LOG.info('Kerberos configuration not found on Jenkins master.')
            LOG.info('You must manually configure any necessary Kerberos '
                     'credentials.')

    def _setup_keytab(self, node):
        """
            Download and setup the keytab for beaker communication if needed
        """
        krb_cfgd = False
        master_ip = self._get_master_ip()
        beaker_config = "/etc/beaker/client.conf"

        LOG.info('Checking Jenkins master for keytab file')
        if common.remote_file_exists(node, master_ip, beaker_config):
            cmd_out = node.cmd("ssh " + master_ip + " \"cat " + beaker_config +
                               " | sed -n" +
                               " 's/^\(KRB_KEYTAB\\s*=\\s*\.*\\)/\\1/p'\"",
                               timeout=120, cmd_list=False)
            if "KRB_KEYTAB" in cmd_out:
                out_lines = cmd_out.splitlines()
                keytab = out_lines[0].replace(' ', '')
                keytab = keytab.replace('KRB_KEYTAB=', '')
                keytab = keytab.replace('"', '')
                if keytab:
                    LOG.info('Keytab found in Jenkins master beaker client'
                             ' config: %s', keytab)
                    if common.remote_file_exists(node, master_ip, keytab):
                        """ Copy keytab file from master to slave
                        """
                        LOG.info('Copying keytab file from Jenkins master')
                        node.cmd("scp %s:%s /etc" % (master_ip, keytab),
                                 timeout=120, cmd_list=False)
                        krb_cfgd = True
        if not krb_cfgd:
            LOG.info('Keytab configuration not performed.')
            LOG.info('To use Beaker, you must manually configure the Beaker'
                     ' client and any necessary Kerberos credentials.')

    def _kill_jslave_procs(self, node):
        """
            Kill processes specified in jslave_procs
        """
        for proc in self.jslave_procs:
            node.cmd('pkill -f %s' % proc)
            LOG.info("Killed proc %s on node %s" % proc, node)

    def _get_master_ip(self):
        url = urlparse.urlsplit(self.jenkins_url)
        return url.netloc


class TeardownJslave(taskrunner.Task):
    """Teardown and kill swarm process on the slave
    """
    def __init__(self, jslave_procs=None, **kwargs):
        """
        :param jslave_procs: list of processes to kill
        This was mainly created since the jenkins
        slave is still showing up on the master even after
        it is deleted
        """
        super(TeardownJslave, self).__init__(**kwargs)
        self.jslave_procs = jslave_procs

    def run(self, context):
        node = context['nodes'].nodes[0]
        ip = context['nodes'].floating_ips[0]

        self._kill_jslave_procs(node)

        LOG.info('Teardown is done running on %s' % ip)

    def cleanup(self, context):
        pass

    def _kill_jslave_procs(self, node):
        """
            Kill processes specified in jslave_procs
        """
        for proc in self.jslave_procs:
            # (proc_status, pids) = node.getPidByName(proc)
            # if proc_status is True:
            node.cmd('pkill -f %s' % proc)
            LOG.info("Killed process %s" % proc)
            # else:
            #     LOG.info("process %s not running" % proc)
