"""Helper functions, later to be moved into job-runner."""

import collections
import copy
import os
import re
import textwrap
import time
import datetime
import logging
from multiprocessing.pool import ThreadPool
import shutil

from job_runner.utilities.machine import CommandExecutionError, runLocalCmd


LOG = logging.getLogger(__name__)
WORKDIR = '~/'
REMOTE_FILES = os.path.join(os.path.dirname(__file__), 'remote_files')

NOSE_OPTS = [
    '-v', '--with-xunit', '--with-id', '--with-xtraceback',
    '--xtraceback-color=off', '--with-openstack', '--openstack-color']
YUM_TIMEOUT = 15*60
PIP_TIMEOUT = 15*60

# groovy script for setting global Jenkins env variables
MASS_ENABLE_GROOVY_SCRIPT = """
for(item in hudson.model.Hudson.instance.items) {
  println("Enabling " + item.name)
  item.disabled = false
  item.save()
}
"""
# groovy script for setting global Jenkins env variables
MASS_DISABLE_GROOVY_SCRIPT = """
for(item in hudson.model.Hudson.instance.items) {
  println("Disabling " + item.name)
  item.disabled = true
  item.save()
}
"""

CFG_JENKINS_CLI_USER = """
import xml.etree.ElementTree as ET
import os
import sys

JENKINS_HOME = "%s"

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
            for sid in role.getiterator("sid"):
                user_cfg_file = user_config_path + sid.text + "/config.xml"
                usertree = ET.parse(user_cfg_file)
                userroot = usertree.getroot()
                keyroot = userroot.find("properties")
                keys = keyroot.getiterator("authorizedKeys")
                if keys:
                    for key in keys:
                        if pub_key not in str(key.text):
                            if key.text is None:
                                key.text = pub_key
                            else:
                                key.text = str(key.text) + pub_key
                        usertree.write(user_cfg_file, encoding="UTF-8")
                else:
                    prop = userroot.find("properties")
                    ssh_auth = ET.SubElement(prop,
                                             "org.jenkinsci.main.modules"
                                             ".cli.auth.ssh."
                                             "UserPropertyImpl")
                    auth_key = ET.SubElement(ssh_auth, "authorizedKeys")
                    auth_key.text = pub_key
                    usertree.write(user_cfg_file, encoding="UTF-8")
else:
    sys.exit(1)

"""

JENKINS_HOME = "/var/lib/jenkins/"


class GitRepo(object):
    """Basic functionality of git."""
    timeout = 15*60

    def __init__(self, url, branch, server, workdir=WORKDIR):
        self.url = url
        self.branch = branch
        dir = ""
        url_split = url.rstrip('/').split('/')
        while not dir:
            dir = url_split.pop()
            if dir.endswith(".git"):
                dir = dir[:-4]
        self.path = workdir + dir
        # expand possible symlinks or home folder (~/)
        self.path = server.cmd('readlink -f %s' % self.path).strip()
        self.server = server

    def clone(self, recursive=False):
        """Create working copy of repository."""
        cmd = 'git clone %s -q %s %s' % (
            '--recursive' if recursive else '',
            self.url,
            self.path)

        self.server.cmd(cmd, timeout=self.timeout)
        self.checkout(log=True)

    def clone_or_pull(self, recursive=False):
        """Update working copy of repository when it exists, or create it."""
        check_folder_exists = self.server.runCmd(
            '[ -d %s ]' % self.path,
            cmd_list=False)
        if check_folder_exists[0]:
            # repo directory already exists
            self.checkout(log=False)
            self.server.cmd('cd %s && git remote set-url origin %s && '
                            'git pull --ff-only' % (self.path, self.url),
                            timeout=self.timeout)
            self.log_info()
        else:
            LOG.info('Repo folder is not there: %s' % check_folder_exists[1])
            self.clone(recursive)

    def checkout(self, branch_or_commit=None, log=True):
        """Checkout the given refspec/branch or self.branch."""
        if branch_or_commit is None:
            branch_or_commit = self.branch

        cmd = ('cd {dir}'
               ' && git checkout {branch}'  # checkout requested branch/treeish
               # but if we end in detached head (branch is actualy treeish/tag)
               ' && ( ! git status|head -n1|grep -q "detached at"'
               # create our local branch from it, so we have 'clean' state
               ' || git checkout -b {branch})')
        cmd = cmd.format(**{'branch': branch_or_commit, 'dir': self.path})
        self.server.cmd(cmd, timeout=self.timeout)
        if log:
            self.log_info()

    def log_info(self):
        """Write info about about current commit into the LOG."""
        self.server.cmd('cd %s'
                        ' && git branch | grep "^\*"'
                        ' && git log -3 --oneline'
                        % self.path,
                        log=True)

    def delete(self):
        """Remove working copy of repository."""
        self.server.cmd("rm -fr %s" % self.path)

    def install(self, extra_params=''):
        """Install the repository as a package using pip.

        Also makes sure that pip is installed.
        """
        pip_cmd = ensure_pip(self.server)
        self.server.cmd("%s install --user -e %s %s"
                        % (pip_cmd, self.path, extra_params),
                        timeout=self.timeout)


class NodeDescriptions(object):
    def __init__(self, data):
        self.data = data

    @property
    def ips(self):
        """List of internal IPs of all nodes."""
        return [n["ip"] for n in self.data]

    @property
    def floating_ips(self):
        """List of floating IPs of nodes that have them."""
        return [n["floating_ip"] for n in self.data
                if n["floating_ip"] is not None]

    @property
    def floating_ips_all_nodes(self):
        """List of floating IPs of all nodes, None where there is no fl.IP."""
        return [n["floating_ip"] for n in self.data]

    @property
    def only_internal_ips(self):
        """List of IPs to nodes that don't have a floating IP"""
        return [n["ip"] for n in self.data
                if n["floating_ip"] not in self.floating_ips]

    @property
    def nodes(self):
        """List of objects that make the nodes accessible trough SSH.

        Not all nodes have to have one.
        """
        return [n['server'] for n in self.data if 'server' in n]

    @property
    def main_node(self):
        """First node object making it accessible trough SSH."""
        return self.nodes[0]

    def __str__(self):
        result = []
        for i, node in enumerate(self.data, 1):
            desc = 'NODE%d:' % i
            if 'floating_ip' in node:
                desc += ' floating ip %s,' % node['floating_ip']
            desc += ' ip %s' % node['ip']
            result.append(desc)
        return ', '.join(result)

    def replace_node_vars(self, text, all_ips=None, separator=', '):
        """Replace strings NODE1/2 ... ALL_NODES in the given text with IPs.

        If all_ips is not provided (list of IP as string), self.ips is used.

        Node numbers are from 1 to len(all_ips).

        It's possible to use also NODES_X+ as to-be-replaced key,
        which contains nodes from X to len(all_ips).
        NODES_X+ sets are also available
        from 1 (NODES_1+==ALL_NODES), to len(all_ips) (==just one ip).
        """
        if all_ips is None:
            all_ips = self.ips

        substitutes = {}
        partial_substitutes = {}

        substitutes['ALL_NODES'] = separator.join(all_ips)
        for n_id, n_ip in enumerate(all_ips, 1):
            # replace all NODE1, NODE2 ... with corresponding IPs
            substitutes['NODE%s' % n_id] = n_ip
            for previous in partial_substitutes:
                partial_substitutes[previous].append(n_ip)
            partial_substitutes['NODES_%s+' % n_id] = [n_ip]

        for subset in partial_substitutes:
            substitutes[subset] = separator.join(partial_substitutes[subset])

        return replace_deep(text, substitutes)

    def ips2nodes(self, ips, floating=False):
        ip_type = 'floating_ip' if floating else 'ip'
        return [n['server'] for n in self.data
                if n[ip_type] in ips]


def replace_deep(subject, replacements):
    """Replace all replacements.keys with their values in subject.

    Always returns copy of the subject, and replaces recursively
    inside the subject.
    """
    replaced = copy.deepcopy(subject)
    if not replacements or not len(replacements):
        return replaced

    if isinstance(subject, str):
        for sub_key, sub_val in replacements.items():
            replaced = replaced.replace(sub_key, sub_val)
    elif isinstance(subject, collections.MutableMapping):
        replaced = dict([
            (k, replace_deep(v, replacements))
            for k, v
            in subject.iteritems()])
    elif isinstance(subject, collections.Sequence):
        replaced = [replace_deep(v, replacements)
                    for v in subject]

    return replaced


def file_exists(node, file_path):
    """Return True if file exists on the node."""
    return node.runCmd("[ -f %s ]" % file_path, cmd_list=False)[0]


def directory_exists(node, dir_path):
    """Return True if the directory on the node."""
    return node.runCmd("[ -d %s ]" % dir_path, cmd_list=False)[0]


def remote_file_exists(node, remote_host, file_path):
    """Return True if file exists on the node."""
    return node.runCmd("ssh %s test -e %s" %
                       (remote_host, file_path),
                       timeout=120, cmd_list=False)[0]


def touch(path):
    basedir = os.path.dirname(path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    with open(path, 'a'):
        os.utime(path, None)


def ensure_pip(node):
    """Find or install pip

    Returns the name of the pip command (tends to be either 'pip' or
    'python-pip').
    """
    try:
        pip = node.cmd('(which pip-python || which pip) 2>/dev/null').strip()
    except CommandExecutionError:
        node.cmd('easy_install pip', log_per_line=True, timeout=120)
        pip = 'pip'
    return pip


def install_packages(node, packages=None, pip_packages=None):
    """Install yum and/or pip packages on node.

    :param packages: List of yum packages
    :param pip_packages: List of pip packages. Items starting with '#' get
        ignored and they can be in the standard pip format (e.g.
        package>=version). Ensures pip is installed.
    """
    if packages:
        packages = ' '.join(packages)
        node.cmd('yum install -y %s' % packages,
                 timeout=YUM_TIMEOUT,
                 log_per_line=True)
    if pip_packages:
        # ignore comments and empty items, add quotemarks around them
        pip_packages = ' '.join(['"%s"' % p.strip() for p in pip_packages
                                 if p and not p.startswith('#')])
        pip_cmd = ensure_pip(node)
        node.cmd('%s install %s' % (pip_cmd, pip_packages),
                 timeout=PIP_TIMEOUT,
                 log_per_line=True)


def check_for_existing_https_cfg(node, node_ip):
    """ Checks if Jenkins is already configured to use HTTPS

    returns True if the Jenkins config file indicates an HTTPS
    configuration
    """
    port_cmd = ('grep -e "^JENKINS_HTTPS_PORT='
                '[\\\'|\\\"]*8443[\\\'|\\\"]*" /etc/sysconfig/jenkins')
    args_cmd = ('grep -e \"^JENKINS_ARGS=[\\\'|\\\"]*.*'
                'httpsKeyStore.*[\\\'|\\\"]*\" /etc/sysconfig/jenkins')

    LOG.info("Checking if Jenkins is configured to use HTTPS...")
    LOG.info("Running command on %s: %s", node_ip, port_cmd)
    https_port_found = node.runCmd(port_cmd,
                                   cmd_list=False)[0]
    LOG.info("Running command on %s: %s", node_ip, args_cmd)
    jenkins_args_found = node.runCmd(args_cmd,
                                     cmd_list=False)[0]
    if https_port_found and jenkins_args_found:
        # if https already enabled, set to True
        return True
    return False


def check_jenkins_global_security(node, node_ip, user, api_token):
    """ Checks if Jenkins global security is enabled

    returns True if the Authorization strategy is anything other
    than Unsecured
    """
    security_enabled = False
    jenkins_cfg = '/var/lib/jenkins/config.xml'
    if not file_exists(node, jenkins_cfg):
        return security_enabled

    security_check_cmd = 'grep "AuthorizationStrategy\$Unsecured" %s' \
                         % jenkins_cfg
    LOG.info("Running command on %s: %s", node_ip, security_check_cmd)
    rc = node.runCmd(security_check_cmd, cmd_list=False)[0]
    if not rc:
        security_enabled = True
    if security_enabled and (user == "" or api_token == ""):
        err_msg = ("Global security is enabled on %s. A Jenkins admin"
                   " user and API token must be specified." % node_ip)
        raise Exception(err_msg)
    return security_enabled


def get_jenkins_cli(node):
    """ Downloads the Jenkins CLI jar to the given node
    """
    if file_exists(node, 'jenkins-cli.jar'):
        return
    cmd = ('wget --no-check-certificate '
           'http://localhost/jnlpJars/jenkins-cli.jar')
    node.cmd(cmd)


def get_jenkins_cli_cmd(node):
    """ Generates Jenkins CLI command based on the protocol Jenkins
    is configured to use

    returns the Jenkins CLI command
    """
    if node.runCmd('grep 8443 /etc/sysconfig/jenkins', cmd_list=False)[0]:
        protocol = 'https'
    else:
        protocol = 'http'
    return 'java -jar jenkins-cli.jar -s %s://localhost/ ' \
        '-noCertificateCheck' % protocol


def config_jenkins_cli_user(node):
    """ Configures Jenkins admin users to allow execution of Jenkins
    CLI commands when Jenkins global security is enabled
    """
    script_name = 'cfg-jenkins-cli-user.py'
    script = CFG_JENKINS_CLI_USER % JENKINS_HOME
    node.cmd("echo '%s' > %s" % (script,
                                 script_name))
    LOG.info("Configuring Jenkins CLI User...")
    admin_role_found = node.runCmd('python {0}'.format(script_name),
                                   cmd_list=False)[0]
    if not admin_role_found:
        err_msg = ('Unable to configure authorized user for Jenkins CLI.'
                   ' Roles-based authentication is not enabled.  Ensure the'
                   ' Role-based Authorization Strategy plugin is installed'
                   ' and a user is configured with the admin role.')
        raise Exception(err_msg)


def create_jobs(node, jobs_repo, jobs_branch, https_enabled=False,
                user=None, api_token=None, force=False,
                ):
    repo = GitRepo(jobs_repo, jobs_branch, node)
    repo.clone_or_pull()
    config_path = "%s/jobs/config" % repo.path
    if https_enabled:
        node.cmd("sed -i 's/^url=http:/url=https:/' %s"
                 % config_path)
    if user is not None:
        node.cmd("sed -i 's/^user=.*/user=%s/' %s"
                 % (user, config_path))
    if api_token is not None:
        node.cmd("sed -i 's/^password=.*/password=%s/' %s"
                 % (api_token, config_path))

    if force:
        node.cmd("jenkins-jobs --ignore-cache --conf %s update "
                 "%s/jobs/" % (config_path, repo.path))
    else:
        node.cmd("jenkins-jobs --conf %s update %s/jobs/"
                 % (config_path, repo.path))


def enable_jobs(node):
    script_name = 'groovy_mass_enable.java'
    node.cmd("echo '%s' > %s" % (MASS_ENABLE_GROOVY_SCRIPT,
                                 script_name))
    LOG.info("Enabling all jobs...")
    jenkins_cli = get_jenkins_cli_cmd(node)
    node.cmd(jenkins_cli + ' groovy ' + script_name,
             timeout=(6 * 60),
             log_per_line=True)


def disable_jobs(node):
    script_name = 'groovy_mass_disable.java'
    node.cmd("echo '%s' > %s" % (MASS_DISABLE_GROOVY_SCRIPT,
                                 script_name))
    LOG.info("Disabling all jobs...")
    jenkins_cli = get_jenkins_cli_cmd(node)
    node.cmd(jenkins_cli + ' groovy ' + script_name,
             timeout=(6 * 60),
             log_per_line=True)


def copy_results_back(node, results_file,
                      dest_dir="~/", filename=None):
    """Copy the results file from node to localhost:dest_dir."""
    if filename is None:
        filename = os.path.basename(results_file)
    dest_path = os.path.join(dest_dir, filename)
    LOG.info('Results stored localy as %s', dest_path)
    node.copyFrom(results_file, dest_path)


def _get_boot_time(node):
    """Calcualte the instance boot time from the current time and from the
       /proc/uptime which contains the seconds since booting."""
    return int(node.cmd("expr `date +%s` - `cut -f1 -d. /proc/uptime`"))


def reboot_nodes(nodes, timeout=10*60):
    """Reboot the nodes and wait until they are connective again."""
    if not nodes:
        return
    old_boot_time = {}
    for node in nodes:
        old_boot_time[node.host] = _get_boot_time(node)
        LOG.info('Rebooting node "%s"', node.host)
        try:
            node.cmd('reboot')
        except CommandExecutionError:
            # reboot can cause immediate connection termination
            LOG.debug("Rebooting..")
    # without the sleep, it would still see the node as connective
    # before it actually rebooted
    time.sleep(15)
    wait_for_ssh(nodes, timeout)
    for node in nodes:
        new_boot_time = _get_boot_time(node)
        LOG.info("booted at node(%s) old/new: %d/%d", node.host,
                 old_boot_time[node.host], new_boot_time)
        # If the machine really rebooted it should have significantly
        # greater boot time
        assert old_boot_time[node.host] + 1 < new_boot_time
        if 'exists' in node.cmd('[ -e /root/soft_lockup.py ] && echo exists'):
            start_latency_meter(node)


def _update_node(params):
    node = params['node']
    if update_system:
        node.cmd('yum update -y', timeout=30*60, log_per_line=True)
    else:
        node.cmd('yum update -y kernel', timeout=15*60, log_per_line=True)
    if not params['reboot_always'] and params['reboot_on_kernel_update']:
        running = node.cmd('uname --kernel-release').strip()
        available = node.cmd('rpm -q kernel --last').split()[0]
        available = available[len("kernel-"):]
        if running != available:
            reboot_nodes([node])
    elif params['reboot_always']:
        reboot_nodes([node])
    return True


def update_system(nodes, system_update=True,
                  reboot_always=True,
                  reboot_on_kernel_update=False):
    """Update system and reboot, wait until connective again.

    Optionally update just the kernel.
    Reboot can be done always, just on kernel update, or not at all.
    """
    p = ThreadPool((min(len(nodes), 32)))
    update_targets = []
    for node in nodes:
        entry = {'system_update': system_update,
                 'reboot_always': reboot_always,
                 'reboot_on_kernel_update': reboot_on_kernel_update,
                 'node': node}
        update_targets.append(entry)

    result = p.map(_update_node, update_targets)
    if not all(result):
        raise RuntimeError("Full system update incomple!")


def wait_for(label, condition, obj_getter, timeout_sec=120, wait_sec=1):
    """Wait for condition to be true until timeout.

    :param label: used for logging
    :param condition: function that takes the object from obj_getter and
        returns True or False
    :param obj_getter: function that returns the object on which the condition
        is tested
    :param timeout_sec: how many seconds to wait until a TimeoutError
    :param wait_sec: how many seconds to wait between testing the condition
    :raises: TimeoutError when timeout_sec is exceeded
             and condition isn't true
    """
    obj = obj_getter()
    timeout = datetime.timedelta(seconds=timeout_sec)
    start = datetime.datetime.now()
    LOG.info('%s - START' % label)
    while not condition(obj):
        if (datetime.datetime.now() - start) > timeout:
            raise TimeoutError(label, timeout_sec)
        time.sleep(wait_sec)
        obj = obj_getter()
    LOG.info('%s - DONE' % label)
    return obj


def ping_nodes(ips, count=3):
    """Ping all the ips 'count' times and log output"""
    for ip in ips:
        rc, out = runLocalCmd(['ping', str(ip), '-c %s' % count])
        LOG.info('Ping on %s:\n%s' % (ip, out))


def _node_hello(node):
    """Check if we can execute commands on the node."""
    output = node.cmd('uname -a; uptime')
    # If we ever use anything else than linux with uname support,
    # it needs to be a format validation
    if 'Linux' not in output:
        raise UnameFormatError


def wait_for_ssh(nodes, timeout=3*60):
    """Wait until all of the IPs give are accessible trough SSH.

    TODO: check accessibility of nodes that don't have a floating IP using
    some SSH accessible node as a proxy
    """
    LOG.info('Waiting for SSH access to nodes')
    for node in nodes:
        wait_for('node %s' % node.host,
                 lambda node: node.isConnective(),
                 lambda: node,
                 timeout,
                 wait_sec=5)

        for i in xrange(32):
            try:
                _node_hello(node)
            except CommandExecutionError as exc:
                LOG.info('uname failed on %s with %s' % (node, exc))
                time.sleep(5)
            except UnameFormatError:
                LOG.warning('Not expected output from uname')
                time.sleep(1)
            else:
                break
        else:
            _node_hello(node)


def openstack_config(node, action, conf_file, section, key, value=''):
    '''Wrapping openstack-config command

    :param node: node on which openstack-config will be called
    :param action: either --set or --get
    :param conf_file: name of the config file that will be modified
    :param section: section in the config file
    :param key: key of the variable
    :param value: value of the variable
    :returns: Output of openstack-config command
    :raises: CommandExecutionError when command fails'''
    return node.cmd("openstack-config %s '%s' '%s' '%s' '%s'"
                    % (action, conf_file, section, key, value))


def puddle_version(node, repo='/etc/yum.repos.d/puddle.repo'):
    url = node.cmd('grep ^baseurl %s 2>/dev/null || echo ""' % repo)
    match = re.match('.*/([\d.-]{10,}|latest)', url)
    if match:
        return match.group(1)


def do_with_all_nodes(nodes, func, *args, **kwargs):
    """Call the same function an all nodes."""
    for node in nodes:
        func(node, *args, **kwargs)


def cmd_all_nodes(nodes, *args, **kwargs):
    """Execute the same command an all nodes."""
    def _cmd_func(node, *args, **kwargs):
        node.cmd(*args, **kwargs)
    do_with_all_nodes(nodes, _cmd_func, *args, **kwargs)


class TimeoutError(Exception):
    def __init__(self, label, timeout=None):
        if timeout is None:
            super(TimeoutError, self).__init__('Timeout of %s' % label)
        else:
            super(TimeoutError, self).__init__('Timeout of %s exceeded %ss'
                                               % (label, timeout))


class UnameFormatError(Exception):
    pass


def file2remote(local_file, remote, remote_path):
    remote.copyTo(os.path.join(REMOTE_FILES, local_file),
                  os.path.join(remote_path, os.path.basename(local_file)))


def start_latency_meter(node):
    node.cmd(". /etc/init.d/functions; "
             "daemon --pidfile /tmp/lockup.pid "
             "setsid python /root/soft_lockup.py "
             "--file /var/log/soft_lockup.log &>/dev/null </dev/null & "
             "exit 0")


def local_log(context, log_file_path):
    context.setdefault('log_callbacks', []).append(
        lambda ctx, logdir: shutil.copy(log_file_path, logdir))


def selinux_enabled(node):
    return node.cmd("getenforce").strip() == 'Enforcing'


def apply_selinux_module(node, name, content):
    node.cmd(('echo "{content}" > {name}.te;'
              ' checkmodule -M -m -o {name}.mod {name}.te;'
              ' semodule_package -o {name}.pp -m {name}.mod;'
              ' semodule -i {name}.pp').format(**{'content': content,
                                                  'name': name}),
             log_per_line=True)


# utilities for packdevstack and devstack

def __item_local_conf(key, val):
    if isinstance(val, list):
        val = ','.join(val)
    return ("%s='%s'" + os.linesep) % (key, str(val))


def local_conf_to_str(conf):
    conf_str = ""
    for (section, keyval) in conf.iteritems():
        conf_str += ('[[%s]]' + os.linesep) % section
        for (key, val) in keyval.iteritems():
            if isinstance(val, dict):
                conf_str += '[%s]' % key
                for (skey, sval) in val.iteritems():
                    conf_str += __item_local_conf(skey, sval)
            else:
                conf_str += __item_local_conf(key, val)
    return conf_str


def deep_conf_patch(d1, d2):
    composed = copy.deepcopy(d1)
    for (section, keyval) in d2.iteritems():
        if section in d1:
            composed[section].update(keyval)
        else:
            composed[section] = copy.deepcopy(keyval)
    return composed


def reload_service(node, service, timeout=3*60):
    # NOTE Using force-reload incorrectly starts the stopped service, which can
    # hide bugs related to chkconfig defaults.
    #
    # Bug 1067025 - The init script actions reload and force-reload are not
    # implemented correctly.
    LOG.warning("Workaround: force-reloading instead of reloading "
                "the service configuration.")
    node.cmd("service '{0}' status && service '{0}' restart".format(service),
             timeout=timeout)


def openstack_service_action(node, action, service, timeout=3*60):
    node.cmd('openstack-service %s %s' % (action, service), timeout=timeout)


def fetch_bm_nics(node):
    """Fetch known eth ifcs as detected by foreman/puppets.

    At the moment these files are only created by
    *sortnics* puppet class in theforeman.eng.lab.tlv.redhat.com.

    :rtype: dict like {'ETH_MANAGEMENT': 'eth0', 'ETH_VLAN': 'eth3'}
    """
    nics = {}
    for eth_type in ('ETH_MANAGEMENT', 'ETH_VLAN', 'ETH_EXT'):
        ifc = node.cmd('[[ -f ~/%s ]] && cat ~/%s || echo ""'
                       % (eth_type, eth_type))
        ifc = ifc.strip()
        if ifc:
            # workaround for a bug in detection
            # unless one ifc is detected as correct one
            # all non-management ifaces are put in
            # the file as a 'eth1eth2eth3' string
            multi = re.findall('eth[0-9]+', ifc)
            if len(multi) > 1:
                ifc = multi[0]

            nics[eth_type] = ifc
    return nics


def kill_security(node):
    node.cmd('sudo setenforce 0',  use_pty=True)
    try:
        node.cmd('sudo service iptables stop',  use_pty=True)
    except CommandExecutionError as ex:
            if "Unit iptables.service not loaded" not in str(ex):
                raise


def ssh_migrate(nodes, nova_user):
        generator_node = nodes[0]
        distribute_nodes = nodes
        generator_node.cmd('[[ -f nova_ssh_id_rsa ]] || '
                           'ssh-keygen -q -t rsa -f nova_ssh_id_rsa -N "";')
        LOG.info('Getting key content from %s' % generator_node.host)
        keys = generator_node.cmd('cat nova_ssh_id_rsa.pub nova_ssh_id_rsa',
                                  log=False)
        keys = keys.split('\n')
        pubkey = keys[0]
        privkey = '\n'.join(keys[1:])
        do_with_all_nodes(
            distribute_nodes, _allow_ssh_for_nova, nova_user, pubkey, privkey)


def _allow_ssh_for_nova(node, nova_user, pubkey, privkey):
    try:
        home = node.cmd('getent passwd "%s"' % nova_user).split(':')[5]
    except CommandExecutionError:
        LOG.info('Nova user not found so skipping host: %s'
                 % node.host)
        return
    LOG.info('Deploying ssh keys on %s' % node.host)
    node.cmd(
        'chsh -s /bin/bash {user}'
        ' && mkdir -p {home}/.ssh'
        ' && echo "{privkey}" > {home}/.ssh/id_rsa'
        ' && echo "{pubkey}" >> {home}/.ssh/authorized_keys'
        ' && chown {user}:{user} -R {home}/.ssh'
        ' && chmod 755 {home}/.ssh'
        ' && chmod 644 {home}/.ssh/authorized_keys'
        ' && chmod 600 {home}/.ssh/id_rsa'
        .format(privkey=privkey, pubkey=pubkey, home=home, user=nova_user),
        log=False
    )

    if not selinux_enabled(node):
        return

    serule = """
        module nova_ssh 1.0;
        require {
            type nova_var_lib_t;
            type sshd_t;
            class dir { getattr search };
        }
        allow sshd_t nova_var_lib_t:dir getattr;
        allow sshd_t nova_var_lib_t:dir search;
    """
    node.cmd('chcon -t ssh_home_t -R %s/.ssh;' % home)
    apply_selinux_module(node, 'nova_ssh', textwrap.dedent(serule))


def bits2netmask(bits):
    bitstr = (int(bits) * '1').ljust(32, '0')
    nums = [bitstr[:8], bitstr[8:16], bitstr[16:24], bitstr[24:]]
    nums = [str(int(num, 2)) for num in nums]
    return '.'.join(nums)
