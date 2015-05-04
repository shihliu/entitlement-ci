import logging
import taskrunner

from tasks import common

LOG = logging.getLogger(__name__)

CHECK_FOR_AUTH_CLI_USER = """
import xml.etree.ElementTree as ET
import os
import sys

JENKINS_HOME = "/var/lib/jenkins/"

jenkins_config = JENKINS_HOME + "config.xml"
user_config_path = JENKINS_HOME + "users/"
tree = ET.parse(jenkins_config)
root = tree.getroot()
roles = root.getiterator("role")
if roles:
    for role in roles:
        name = role.attrib.get("name")
        if name == "admin":
            pub_key = os.popen("cat ~/.ssh/id_rsa.pub").read()
            admin_user_exists = False
            for sid in role.getiterator("sid"):
                user_cfg_file = user_config_path + sid.text + "/config.xml"
                usertree = ET.parse(user_cfg_file)
                userroot = usertree.getroot()
                keyroot = userroot.find("properties")
                keys = keyroot.getiterator("authorizedKeys")
                if keys:
                    for key in keys:
                        key_value = key.text
                        if not key_value is None:
                            if str(pub_key) in str(key_value):
                                admin_user_exists = True
            if admin_user_exists:
                sys.exit(0)
sys.exit(1)
"""


class ManageJobs(taskrunner.Task):
    """Install and configure Jenkins, create jobs with job-builder.
    """

    def __init__(self, update_jobs=False, force_update=False, jobs_repo=None,
                 jobs_branch='master', enable_all_jobs=False,
                 disable_all_jobs=False, jenkins_user=None, api_token=None,
                 **kwargs):
        """
        :param update_jobs: if True, update jobs using job-builder from the
            definitions in jobs_repo
        :param jobs_repo: git repository that will be used by
            jenkins-job-builder that has a 'jobs/' directory with a file called
            'config' containing the credentials for Jenkins and yaml files with
            the job definitions.
        :param jobs_branch: branch of the `jobs_repo` git repository
        :param enable_all_jobs: if true, all jobs will be enabled
        :param disable_all_jobs: if true, all jobs will be disabled
        :param jenkins_user: Jenkins admin user
        :param api_token: API token for Jenkins admin user authentication
        """
        super(ManageJobs, self).__init__(**kwargs)
        self.update_jobs = (str(update_jobs) == 'True')
        self.force_update = (str(force_update) == 'True')
        self.jobs_repo = jobs_repo
        self.jobs_branch = jobs_branch
        self.enable_all_jobs = (str(enable_all_jobs) == 'True')
        self.disable_all_jobs = (str(disable_all_jobs) == 'True')
        self.jenkins_user = jenkins_user
        self.api_token = api_token
        self.security_enabled = False
        self.https_enabled = False

    def run(self, context):
        for i in range(len(context['nodes'].nodes)):
            node = context['nodes'].nodes[i]
            ip = context['nodes'].floating_ips[i]

            self.security_enabled = \
                common.check_jenkins_global_security(node, ip,
                                                     self.jenkins_user,
                                                     self.api_token)
            self.https_enabled = \
                common.check_for_existing_https_cfg(node, ip)

            if self.security_enabled and \
                    (self.enable_all_jobs or self.disable_all_jobs):
                self._check_for_auth_cli_user(node, ip)
            common.get_jenkins_cli(node)
            self._update_jobs(node)
            self._enable_jobs(node)
            self._disable_jobs(node)
            LOG.info('Jenkins jobs updated at http://' + ip)

    def cleanup(self, context):
        pass

    def _check_for_auth_cli_user(self, node, node_ip):
        """
        Verify that there is a Jenkins admin user configured with the master's
        SSH public key
        """
        script_name = 'check_auth_cli_user.py'
        node.cmd("echo '%s' > %s" % (CHECK_FOR_AUTH_CLI_USER,
                                     script_name))
        auth_user_found = node.runCmd('python {0}'.format(script_name),
                                      cmd_list=False)[0]
        if not auth_user_found:
            err_msg = ("Global security is enabled on %s. Ensure Role-Based"
                       " Authentication is enabled and at least one"
                       " Jenkins admin user is configured with the"
                       " SSH Public Key set to the master's public key"
                       " if you wish to perform Enable/Disable"
                       " operations." % node_ip)
            raise Exception(err_msg)

    def _update_jobs(self, node):
        """Create jobs using jenkins-job-builder
        """
        if not self.update_jobs:
            return
        common.create_jobs(node, self.jobs_repo, self.jobs_branch,
                           self.https_enabled, self.jenkins_user,
                           self.api_token, self.force_update)

    def _enable_jobs(self, node):
        if not self.enable_all_jobs:
            return
        common.enable_jobs(node)

    def _disable_jobs(self, node):
        if not self.disable_all_jobs:
            return
        common.disable_jobs(node)
