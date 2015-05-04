import logging
import os
import random
import taskrunner
import urllib
import xml.etree.ElementTree as ET
from job_runner.utilities.machine import CommandExecutionError

from tasks import common

LOG = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
VIEW_LABEL = os.environ.get('VIEW_LABEL', 'Results Dashboard')
VIEW_FILTER = os.environ.get('VIEW_FILTER', '.*')


# repository with taskrunner tasks shared among QE teams
QETASKS_REPO = 'git://git.app.eng.bos.redhat.com/qetasks.git'

# Jenkins plugins needed by this task
REQUIRED_PLUGINS = ['groovy']

# groovy script for setting global Jenkins env variables
SET_ENV_GROOVY_SCRIPT = """
def hudson = hudson.model.Hudson.instance
def globalProps = hudson.globalNodeProperties
if(globalProps.size() != 1) {
    globalProps.replaceBy(
        [new hudson.slaves.EnvironmentVariablesNodeProperty()])
}
def props = globalProps.getAll(
    hudson.slaves.EnvironmentVariablesNodeProperty.class)
for (prop in props) {
    // add prop.envVars.put(key, value)
    %s
}
hudson.save()
"""

MASS_DISABLE_GROOVY_SCRIPT = """
for(item in hudson.model.Hudson.instance.items) {
  println("Disabling " + item.name)
  item.disabled = true
  item.save()
}
"""

# groovy script to set global Jenkins properties
SET_GLOBAL_CFG_GROOVY_SCRIPT = """
def hudson = hudson.model.Hudson.instance

def ds = hudson.getExtensionList(jenkins.model.DownloadSettings.class)[0]
ds.setUseBrowser(false)
ds.save()

"""

CFG_UPDATE_SITE_PYTHON_SCRIPT = """
import xml.etree.ElementTree as ET

JENKINS_HOME = "%s"
rh_ctr_exists = False

update_ctr_config = JENKINS_HOME + "hudson.model.UpdateCenter.xml"
tree = ET.parse(update_ctr_config)
root = tree.getroot()
for sites in root.getiterator("sites"):
    for id in sites.getiterator("id"):
        if id.text == "redhat-update-center":
            rh_ctr_exists = True
    if not rh_ctr_exists:
        site = ET.Element("site")
        siteid = ET.SubElement(site, "id")
        siteid.text = "redhat-update-center"
        url = ET.SubElement(site, "url")
        url.text = "http://ci-ops-jenkins-update-site.rhev-ci-vms.eng." \
            "rdu2.redhat.com/jenkins-update-center/update-center.json"
        sites.append(site)
tree.write(update_ctr_config, encoding="UTF-8")
"""

JENKINS_HOME = '/var/lib/jenkins/'


class CreateJenkins(taskrunner.Task):
    """Install and configure Jenkins, create jobs with job-builder.
    """

    def __init__(self, plugins=None, install_citools=False,
                 citools_repo=None, citools_branch='master',
                 create_jobs=False, install_qetasks=False,
                 jobs_repo=None, jobs_branch='master', rpm_deps=None,
                 pip_deps=None, jobs_enabled=True, cfg_results_view=False,
                 ssh_keyfile=None, jenkins_env_vars=None,
                 https_enabled=False, ssl_cert=None, ssl_key=None,
                 keystore_pass=None, jenkins_user=None, api_token=None,
                 **kwargs):
        """
        :param plugins: list of Jenkins plugins that will be installed in
            addition to the `REQUIRED_PLUGINS` list
        :param install_citools: will clone the citools_repo git repository and
            install tools
        :param citools_repo: git repository that will be used to install
            any additional tools/modules needed by the Jenkins master
        :param citools_branch: branch of the `citools_repo` git repository
        :param create_jobs: if True, create jobs using job-builder from the
            definitions in jobs_repo
        :param install_qetasks: will clone the qetasks git repository and
            install it using pip
        :param jobs_repo: git repository that will be used by
            jenkins-job-builder that has a 'jobs/' directory with a file called
            'config' containing the credentials for Jenkins and yaml files with
            the job definitions.
        :param jobs_branch: branch of the `jobs_repo` git repository
        :param rpm_deps: list of yum packages needed on the system
        :param pip_deps: list of pip packages needed on the system
        :param jobs_enabled: if the newly created jobs should be left enabled
        :param cfg_results_view: if the results dashboard views will be enabled
        :param ssh_keyfile: path to the file with the private key of `keypair`
        :param https_enabled: HTTPS will be enabled if True
        :param ssl_cert: SSL cert to use for SSL/HTTPS for Jenkins
        :param ssl_key: key used to generate SSL cert used for SSL/HTTPS
            for Jenkins
        :param keystore_pass: password for Jenkins keystore
        :param jenkins_user: Jenkins admin user
        :param api_token: API token for Jenkins admin user authentication
        :param jenkins_env_vars: Jenkins global environment variables that you
            can later find in the UI under:
            `Manage Jenkins -> Configure -> Global properties`
        """
        super(CreateJenkins, self).__init__(**kwargs)
        self.plugins = plugins or []
        self.install_citools = install_citools
        self.citools_repo = citools_repo
        self.citools_branch = citools_branch
        self.create_jobs = create_jobs
        self.install_qetasks = install_qetasks
        self.jobs_repo = jobs_repo
        self.jobs_branch = jobs_branch
        self.rpm_deps = rpm_deps or []
        self.pip_deps = pip_deps or []
        self.jobs_enabled = (str(jobs_enabled) == 'True')
        self.cfg_results_view = cfg_results_view
        self.ssh_keyfile = ssh_keyfile
        self.https_enabled = (str(https_enabled) == 'True')
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.keystore_pass = keystore_pass
        self.jenkins_user = jenkins_user
        self.api_token = api_token
        self.env_vars = jenkins_env_vars
        self.security_enabled = False
        self.https_cfg_exists = False

    def run(self, context):
        for i in range(len(context['nodes'].nodes)):
            node = context['nodes'].nodes[i]
            ip = context['nodes'].floating_ips[i]

            self.security_enabled = \
                common.check_jenkins_global_security(node, ip,
                                                     self.jenkins_user,
                                                     self.api_token)
            self.https_cfg_exists = \
                common.check_for_existing_https_cfg(node, ip)
            if self.https_cfg_exists:
                self.https_enabled = True

            if self.https_enabled:
                self.rpm_deps.append('httpd')

            common.install_packages(node, self.rpm_deps, self.pip_deps)
            self._iptables(node, ip)
            self._config_networking(node, ip)
            self._workaround_java_ssl(node)
            self._add_certificate(node)
            self._upload_ssh_keys(node)

            node.cmd('chkconfig jenkins on')
            self._service_jenkins(node, 'restart')
            common.get_jenkins_cli(node)
            jenkins_cli = common.get_jenkins_cli_cmd(node)
            if self.security_enabled:
                common.config_jenkins_cli_user(node)
                self._service_jenkins(node, 'restart')
            self._set_global_jenkins_cfg(node, jenkins_cli)
            self._install_plugins(node, REQUIRED_PLUGINS + self.plugins,
                                  jenkins_cli)
            self._config_jenkins_backups(node, ip)
            self._config_job_priorities(node)

            self._service_jenkins(node, 'restart')
            self._set_env_vars(node, ip, jenkins_cli)
            self._install_citools(node)
            self._install_qetasks(node)
            self._create_jobs(node)
            self._configure_views(node)
            LOG.info('Jenkins instance created at http://' + ip)

    def cleanup(self, context):
        pass

    def _service_jenkins(self, node, action):
        log = '/var/log/jenkins/jenkins.log'
        node.cmd('[[ -f %s ]] && > %s || :' % (log, log))
        node.cmd('service jenkins %s' % action)
        LOG.info('Waiting for %s of jenkins ...' % action)
        common.wait_for(
            'jenkins',
            lambda node: 'fully up' in node.cmd(
                'grep "fully up and running" %s || :' % log),
            lambda: node,
            timeout_sec=(4 * 60),
            wait_sec=5)

    def _config_networking(self, node, node_ip):
        """Configure Jenkins to use https

        Create/configure to use certificate, as well as configure iptables
        and port forwarding.
        """
        if not self.https_enabled:
            return

        if self.https_cfg_exists:
            # assume jenkins is already configured for https
            LOG.info("Jenkins already configured for HTTPS.")
        else:
            LOG.info("Configuring Jenkins for HTTPS...")

            keystore_dir = JENKINS_HOME + '.ssl'
            node.cmd('mkdir -p {0}'.format(keystore_dir))
            node.cmd('chown jenkins:jenkins {0}'.format(keystore_dir))
            node.cmd('chmod 755 {0}'.format(keystore_dir))
            if self.ssl_cert:
                with open(self.ssl_cert, 'r') as ssl_cert_content:
                    ssl_cert = ssl_cert_content.read()
                with open(self.ssl_key, 'r') as ssl_key_content:
                    ssl_key = ssl_key_content.read()
                node.cmd('echo "%s" > jenkins.crt' % ssl_cert)
                node.cmd('echo "%s" > jenkins.key' % ssl_key)
                node.cmd('cat jenkins.crt | /usr/bin/certutil'
                         ' -d sql:/etc/pki/nssdb -A -t "C,,"'
                         ' -n jenkins-ssl-cert')
                node.cmd('openssl pkcs12 -export -in jenkins.crt'
                         ' -inkey jenkins.key -out jenkins.p12'
                         ' -name jenkins-ssl-cert -CAfile jenkins-ca.crt'
                         ' -caname root -password pass:%s'
                         % self.keystore_pass)
                try:
                    node.cmd('keytool -importkeystore -deststorepass %s'
                             ' -destkeypass %s -destkeystore %s/keystore'
                             ' -srckeystore jenkins.p12 -srcstoretype PKCS12'
                             ' -srcstorepass %s -alias jenkins-ssl-cert'
                             % (self.keystore_pass, self.keystore_pass,
                                keystore_dir, self.keystore_pass))
                except CommandExecutionError, ex:
                    if 'already exists' not in ex.message:
                        raise
            else:
                LOG.info("Creating self-signed certificate...")
                node.cmd('keytool -genkey -alias jenkins-ssl-cert -keyalg RSA'
                         ' -keystore %s/keystore'
                         ' -dname "CN=http://%s, O=Red Hat" -storepass %s'
                         ' -keypass %s -validity 365'
                         % (keystore_dir, node_ip, self.keystore_pass,
                            self.keystore_pass))

            LOG.info("Modifying Jenkins configuration...")
            node.cmd("sed -i"
                     " 's/^JENKINS_PORT=.*"
                     "/JENKINS_PORT=\"-1\"/'"
                     " /etc/sysconfig/jenkins")
            node.cmd("sed -i"
                     " 's/^JENKINS_HTTPS_PORT=.*"
                     "/JENKINS_HTTPS_PORT=\"8443\"/'"
                     " /etc/sysconfig/jenkins")
            node.cmd("sed -i"
                     " 's/^JENKINS_ARGS=.*"
                     "/JENKINS_ARGS="
                     "\"--httpsKeyStore=\/var\/lib\/jenkins\/.ssl\/keystore"
                     " --httpsKeyStorePassword=%s\"/'"
                     " /etc/sysconfig/jenkins"
                     % (self.keystore_pass))

            LOG.info("Configuring httpd to forward port 80 traffic to "
                     "port 443...")
            rewrite_found = node.runCmd('grep -e "^Rewrite.*" '
                                        '/etc/httpd/conf/httpd.conf',
                                        cmd_list=False)[0]
            if not rewrite_found:
                node.cmd('echo '
                         '"RewriteEngine On" >> /etc/httpd/conf/httpd.conf')
                node.cmd('echo '
                         '"RewriteRule (.*)'
                         ' https://%{HTTP_HOST}%{REQUEST_URI}"'
                         ' >> /etc/httpd/conf/httpd.conf')
            node.cmd('chkconfig httpd on')
            node.cmd('/etc/init.d/httpd start')

    def _iptables(self, node, node_ip):
        """Use port 80 for Jenkins.

        It's more comfortable to use Jenkins on port 80, the simplest way to do
        that is with an iptables redirect on the machine itself.
        """
        node.cmd('service iptables stop')
        node.cmd('cat /dev/null > /etc/sysconfig/iptables')
        node.cmd('service iptables start')
        if not self.https_enabled:
            node.cmd('iptables -A PREROUTING -t nat -i eth0 -p tcp'
                     ' --dport 80 -j REDIRECT --to-port 8080')
            # redirect for the localhost (service jobs need this)
            node.cmd('iptables -t nat -I OUTPUT --src 0/0 --dst 127.0.0.1 -p'
                     ' tcp --dport 80 -j REDIRECT --to-ports 8080')
            # redirect for the real address from localhost
            node.cmd('iptables -t nat -A OUTPUT -p tcp -d %s'
                     ' --dport 80 -j REDIRECT --to-port 8080' % node_ip)
        else:
            node.cmd('iptables -t nat -A PREROUTING -p tcp --dport 443 -j'
                     ' REDIRECT --to-ports 8443')
            # redirect for the localhost (service jobs need this)
            node.cmd('iptables -t nat -A OUTPUT -p tcp --dport 443 -j REDIRECT'
                     ' --to-ports 8443 --destination 127.0.0.1')
            # redirect for the real address from localhost
            node.cmd('iptables -t nat -A OUTPUT -p tcp --dport 443 -j REDIRECT'
                     ' --to-ports 8443 --destination %s' % node_ip)
            node.cmd('service iptables save')

    def _add_certificate(self, node):
        """Add RedHat certificate

        In our corporate environment, we have to add the internal Red Hat CA
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

    def _upload_ssh_keys(self, node):
        """
            Upload a private key to the master
        """
        with open(self.ssh_keyfile, 'r') as ssh_keyfile_content:
            ssh_private_key = ssh_keyfile_content.read()
        node.cmd('echo "%s" > ~/.ssh/id_rsa' % ssh_private_key)
        node.cmd('ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub')
        node.cmd('cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys')

    def _set_global_jenkins_cfg(self, node, jenkins_cli):
        script_name = 'groovy_set_jenkins_cfg.java'
        node.cmd("echo '%s' > %s" % (SET_GLOBAL_CFG_GROOVY_SCRIPT,
                                     script_name))
        node.cmd(jenkins_cli + ' groovy ' + script_name)

    def _config_update_sites(self, node):
        """
        Configure custom update sites
        """
        local_path = os.path.join(THIS_DIR, 'remote_files')
        cert_file = 'redhat-update-center.crt'

        script_name = 'cfg_update_site.py'
        script = CFG_UPDATE_SITE_PYTHON_SCRIPT % JENKINS_HOME
        node.cmd("echo '%s' > %s" % (script,
                                     script_name))
        node.cmd('python ' + script_name)
        rem_cert_path = JENKINS_HOME + 'update-center-rootCAs'
        node.cmd('mkdir -p {0}'.format(rem_cert_path))
        common.file2remote(os.path.join(local_path, cert_file),
                           node, rem_cert_path)
        node.cmd('chown jenkins:jenkins {0}'.format(os.path.join(rem_cert_path,
                                                                 cert_file)))
        self._service_jenkins(node, 'restart')

    def _install_plugins(self, node, plugins, jenkins_cli):
        """Update plugin list and install `plugins`.
        """

        self._config_update_sites(node)

        update_dir = JENKINS_HOME + 'updates'
        LOG.info('Updating the Jenkins plugin list')
        # get default update center information
        node.cmd('wget -O default.js '
                 'http://updates.jenkins-ci.org/update-center.json')
        node.cmd('sed \'1d;$d\' default.js > default.json')
        # Short-term fix for issue with swarm plugin use version 1.20
        node.cmd('mkdir -p {0}; mv default.json {0};'
                 ' chown -R jenkins:jenkins {0}'.format(update_dir))
        # get redhat-update-center information
        node.cmd('wget -O redhat-update-center.js '
                 'http://ci-ops-jenkins-update-site.rhev-ci-vms.eng.rdu2.'
                 'redhat.com/jenkins-update-center/update-center.json')
        node.cmd('sed \'1d;$d\' redhat-update-center.js > '
                 'redhat-update-center.json')
        node.cmd('mv redhat-update-center.json {0};'
                 ' chown -R jenkins:jenkins {0}'.format(update_dir))

        self._service_jenkins(node, 'restart')

        node.cmd(jenkins_cli + ' install-plugin %s' % ' '.join(plugins),
                 log_per_line=True,
                 timeout=5 * 60)

    def _config_jenkins_backups(self, node, node_ip):
        LOG.info('Configuring Jenkins backups...')

        # determine name of NFS share if it exists and set backup dir
        mnt_cmd = "mount | grep jenkins-results | cut -d' ' -f3"
        LOG.info("Running command on %s: %s", node_ip, mnt_cmd)
        rc, out = node.runCmd(mnt_cmd, cmd_list=False)
        out = out.strip(' \t\n\r')
        if not rc or not out:
            LOG.warn('Backup storage not mounted.'
                     ' Jenkins backups will not be configured.')
            return

        bkup_dir = os.path.join(str(out), '.backups')
        node.cmd('mkdir -p {0}'.format(bkup_dir))
        node.cmd('chown jenkins:jenkins {0}'.format(bkup_dir))
        node.cmd('chmod 755 {0}'.format(bkup_dir))

        local_path = os.path.join(THIS_DIR, 'remote_files')
        orig_cfg = 'thinBackup.xml'
        randint = random.randrange(0, 1000)
        updated_cfg = "temp_" + str(randint) + orig_cfg

        # inject backup dir into thinBackup config file
        tree = ET.parse(os.path.join(local_path, orig_cfg))
        root = tree.getroot()
        # TODO: Using getiterator() since its backward compatible
        # with Python 2.6
        # This is deprectated in 2.7 and we should be using iter()
        for path in root.getiterator('backupPath'):
            path.text = bkup_dir

        tree.write(os.path.join(local_path, updated_cfg), encoding="UTF-8")

        common.file2remote(updated_cfg, node, JENKINS_HOME)
        node.cmd('mv {0} {1}'.format(os.path.join(JENKINS_HOME, updated_cfg),
                                     os.path.join(JENKINS_HOME, orig_cfg)))

        # Clean up temporary config files
        if os.path.isfile(os.path.join(local_path, updated_cfg)):
            os.remove(os.path.join(local_path, updated_cfg))
        LOG.info('Jenkins backup configuration complete.')

    def _config_job_priorities(self, node):
        """
        Configure job priorities for queuing
        """
        pri_cfg = "jenkins.advancedqueue.PriorityConfiguration.xml"
        pri_sort_cfg = "jenkins.advancedqueue.PrioritySorterConfiguration.xml"
        remote_pri_cfg = JENKINS_HOME + pri_cfg

        LOG.info('Checking for existing Job Priorities configuration...')
        job_group_found = node.runCmd('grep jenkins.advancedqueue.JobGroup %s'
                                      % remote_pri_cfg, cmd_list=False)[0]

        # If job groups are already cfg'd, we won't touch the priority config.
        # Otherwise, we write the default priority sorter config files.
        if not job_group_found:
            LOG.info('No existing Job Groups defined.  Writing default '
                     'job priority configuration.')
            common.file2remote(pri_cfg, node, JENKINS_HOME)
            common.file2remote(pri_sort_cfg, node, JENKINS_HOME)
        else:
            LOG.info('Job Group definitions already exist.  Skipping '
                     'job priority configuration.')

    def _set_env_vars(self, node, node_ip, jenkins_cli):
        """Run a groovy script that will will set global env variables
        """
        if not self.env_vars:
            return
        set_cmd = []
        for key, value in self.env_vars.items():
            if 'JENKINS_MASTER_URL' in key:
                if self.https_enabled:
                    set_cmd.append('prop.envVars.put("%s", "https://%s")'
                                   % (key, node_ip))
                else:
                    set_cmd.append('prop.envVars.put("%s", "http://%s")'
                                   % (key, node_ip))
            else:
                set_cmd.append('prop.envVars.put("%s", "%s")' % (key, value))
        script = SET_ENV_GROOVY_SCRIPT % '\n    '.join(set_cmd)
        script_name = 'groovy_set_env.java'
        node.cmd("echo '%s' > %s" % (script, script_name))
        node.cmd(jenkins_cli + ' groovy ' + script_name)

    def _install_citools(self, node):
        """Installs additional tools/modules needed by Jenkins master
        """
        if not self.install_citools:
            return
        node.cmd("pip install --index-url=http://ci-ops-jenkins-update-site."
                 "rhev-ci-vms.eng.rdu2.redhat.com/packages/simple"
                 " jenkins-ci-sidekick")

    def _install_qetasks(self, node):
        """Clones the qetasks git repo and installs it"""
        if not self.install_qetasks:
            return
        repo = common.GitRepo(QETASKS_REPO, 'master', node)
        repo.clone_or_pull()
        pip_cmd = common.ensure_pip(node)
        node.cmd("%s install %s" % (pip_cmd, repo.path), timeout=5 * 60)

    def _create_jobs(self, node):
        """Create jobs using jenkins-job-builder
        """
        if not self.create_jobs:
            return
        common.create_jobs(node, self.jobs_repo, self.jobs_branch,
                           self.https_enabled, self.jenkins_user,
                           self.api_token)
        if not self.jobs_enabled:
            common.disable_jobs(node)

    def _configure_views(self, node):
        """ Create default results dashboard views
        """
        if not self.cfg_results_view:
            return

        # Define base results configuration XML files

        local_path = os.path.join(THIS_DIR, 'remote_files')
        nested_view_cfg = 'resultsConfig.xml'
        summary_view_cfg = 'summaryConfig.xml'
        trend_view_cfg = 'trendConfig.xml'
        randint = random.randrange(0, 1000)
        updated_summary_cfg = "temp_" + str(randint) + summary_view_cfg
        updated_trend_cfg = "temp_" + str(randint) + trend_view_cfg

        # Copy Nested View XML file to Jenkins master

        remote_path = JENKINS_HOME + 'views'
        node.cmd('[[ -d %s ]] || mkdir -p %s' % (remote_path, remote_path))
        common.file2remote(nested_view_cfg, node, remote_path)

        # Configure filter and copy view XML config to Jenkins master

        self._cfg_view_filter(os.path.join(local_path, summary_view_cfg),
                              os.path.join(local_path, updated_summary_cfg))
        self._cfg_view_filter(os.path.join(local_path, trend_view_cfg),
                              os.path.join(local_path, updated_trend_cfg))
        common.file2remote(updated_summary_cfg, node, remote_path)
        common.file2remote(updated_trend_cfg, node, remote_path)

        # Create the views using the config files
        LOG.info('Creating Jenkins default results views')
        if self.https_enabled:
            protocol = "https"
        else:
            protocol = "http"
        if self.security_enabled and self.jenkins_user and self.api_token:
            user_info = "-u %s:%s" % (self.jenkins_user, self.api_token)
        else:
            user_info = ""

        node.cmd(("curl -vvv -k -X POST -d @{0}/{1} -H"
                  " 'Content-Type: text/xml'"
                  " {2}://localhost/createView?name={3} {4}")
                 .format(remote_path, nested_view_cfg, protocol,
                         urllib.quote(VIEW_LABEL), user_info))
        node.cmd(("curl -vvv -k -X POST -d @{0}/{1} -H"
                  " 'Content-Type: text/xml'"
                  " {2}://localhost/view/{3}/createView?"
                  "name=Overall%20Results%20Summary {4}")
                 .format(remote_path, updated_summary_cfg, protocol,
                         urllib.quote(VIEW_LABEL), user_info))
        node.cmd(("curl -vvv -k -X POST -d @{0}/{1} -H"
                  " 'Content-Type: text/xml'"
                  " {2}://localhost/view/{3}/createView?"
                  "name=Result%20Trends%20\(per%20job\) {4}")
                 .format(remote_path, updated_trend_cfg, protocol,
                         urllib.quote(VIEW_LABEL), user_info))

        # Clean up temporary config files

        if os.path.isfile(os.path.join(local_path, updated_summary_cfg)):
            os.remove(os.path.join(local_path, updated_summary_cfg))
        if os.path.isfile(os.path.join(local_path, updated_trend_cfg)):
            os.remove(os.path.join(local_path, updated_trend_cfg))

    def _workaround_java_ssl(self, node):
        """Disable SNI extension.

        http://stackoverflow.com/q/7615645/2859073
        """
        LOG.warning("Workaround: disabling SNI extension in case Java 1.7"
                    " is being used, it causes problems with SSL")
        node.cmd("sed -i"
                 " 's/^JENKINS_JAVA_OPTIONS=.*"
                 "/JENKINS_JAVA_OPTIONS=\"-Djava.awt.headless=true"
                 " -Djsse.enableSNIExtension=false\"/'"
                 " /etc/sysconfig/jenkins")

    def _cfg_view_filter(self, orig_cfg_file, updated_cfg):
        """Configure view filter and return string containing modified
        XML file content
        """
        tree = ET.parse(orig_cfg_file)
        root = tree.getroot()
        # TODO: Using getiterator() since its backward compatible
        # with Python 2.6
        # This is deprectated in 2.7 and we should be using iter()
        for regex in root.getiterator('includeRegex'):
            regex.text = VIEW_FILTER

        tree.write(updated_cfg, encoding="UTF-8")
