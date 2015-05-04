import pprint
import logging
import json
import os.path
from textwrap import dedent
import uuid
import time
import socket
from time import sleep

from job_runner.utilities import machine
import taskrunner

import nodefactory
import common

LOG = logging.getLogger(__name__)

# how long to wait until the nodes are accessible with SSH
SSH_TIMEOUT = 5*60
PREPARED_MARKER = '~/.prepared-by-cic-getnodes'

# Max of attempts to boot a VM with ERROR status
MAX_BOOT_RETRIES = 5

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WRITE_MIME_MULTI = '/usr/bin/write-mime-multipart'
USER_DATA = dedent(r'''
    #cloud-config
    disable_root: 0
    ssh_pwauth: 1

    users:
      - name: root
        lock-passwd: false
        inactive: false
        system: false

    # Resize the root in the background. This saves some time
    # when resizing small image to large image, but it also
    # creates a danger of "No space left on the device."

    # WORKAROUND: https://bugs.launchpad.net/cloud-init/+bug/1080985
    # resize_rootfs: noblock
    resize_rootfs: false
    runcmd:
      - |
        ROOT_DEV=`mount | sed -n 's/^\(\S\+\)\W\+on\W\/\W\+.*/\1/p'`
        echo "Detected root dev: $ROOT_DEV."
        resize2fs "$ROOT_DEV" 2>&1 > /var/log/resize.log &
        touch /cloud_inited
''')

USER_DATA_FILES = [THIS_DIR + '/../cloud-init'
                              '/cloud-config-enable-root-resize-rtpt.txt']


class GetNodesBase(taskrunner.Task):

    def __init__(self, ssh_user='root', ssh_pass='123456',
                 rhn_deregister=False, pypi_mirror='',
                 fedora_mirror=None, fedora_mode=False,
                 ssh_keyfile=None, force_preparation=False,
                 metadata=None, resources_file=None,
                 **kwargs):
        """
        :param ssh_user: user that should connect tho the created node
        :param ssh_pass: not necessary if `ssh_keyfile` is given
        :param ssh_keyfile: path to the file with the private key of `keypair`,
            not necessary if `ssh_pass` is given
        :param pypi_mirror: url for pypi mirror
        :param rhn_deregister: deregister from rhn if true
        :param fedora_mirror: url for mirror with fedora packages
        :param fedora_mode: true if the host is/should be fedora
        :param force_preparation: if True do not skip repeated preparation
        :param metadata: extra parameters used to define resources
        :param resources_file: json file to define resources that are created
        """
        super(GetNodesBase, self).__init__(**kwargs)
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.ssh_keyfile = ssh_keyfile
        # workaround - enforcing mirror
        self.pypi_mirror = pypi_mirror
        self.rhn_deregister = (str(rhn_deregister).lower() == 'true')
        self.force_preparation = (str(force_preparation).lower() == 'true')
        self.fedora_mirror = fedora_mirror
        # TODO: get the facts and use them
        self.fedora_mode = (str(fedora_mode).lower() == 'true')
        self.metadata = metadata
        self.resources_file = resources_file

    def _prepare_nodes(self, desc):
        if (not self.force_preparation
            and '0' == desc.main_node.cmd('[[ -f %s ]]; echo $?'
                                          % PREPARED_MARKER).strip()):
            LOG.info('Skipping preparation as nodes should be already'
                     ' prepared by us.')
            return
        self._prepare_nodes_for_passive_ssh(desc)
        self._pip_config(desc)
        if self.fedora_mode:
            if self.fedora_mirror:
                self._fedora_repo_config(desc)
        else:
            if self.rhn_deregister:
                self._deregister_rhn(desc)
        desc.main_node.cmd('touch %s' % PREPARED_MARKER)

    def _prepare_nodes_for_passive_ssh(self, node_descriptions):
        """Workaround for preparation of non-interactive ssh connections.

        Create new keys on main_node, distribute them to others and allow
        ssh connections without fingerprint/ip verification.

        TODO: do this with cloud-init or other appropriate tool
        TODO: distribute keys to nodes that don't have a floating IP
        """
        LOG.info("Distributing ssh keys between nodes.")
        LOG.warning('Workaround: ssh keys should be hardcoded/prepared in'
                    ' images/or distributed in better (more static) way')
        main = node_descriptions.main_node
        main.cmd('[[ -f ~/.ssh/id_rsa ]] ||'
                 ' ssh-keygen -q -t rsa'
                 ' -f ~/.ssh/id_rsa'
                 ' -N ""')
        pubkey = main.cmd('cat ~/.ssh/id_rsa.pub', log=False)
        privkey = main.cmd('cat ~/.ssh/id_rsa', log=False)
        for node in node_descriptions.nodes:
            self._upload_ssh_keys(node, privkey, pubkey)
            self._allow_unchecked_ssh(node)

    def _upload_ssh_keys(self, node, privkey, pubkey):
        """Upload private and public ssh keys to node."""
        node.cmd('echo "%s" > ~/.ssh/id_rsa' % privkey, log=False)
        node.cmd('echo "%s" > ~/.ssh/id_rsa.pub' % pubkey, log=False)
        node.cmd('echo "%s" >> ~/.ssh/authorized_keys' % pubkey, log=False)
        node.cmd('chmod go-rwx -R ~/.ssh')

    def _allow_unchecked_ssh(self, node):
        """
            Allow ssh from node without server fprint/ip verification.
        """
        node.cmd('echo "Host *\n'
                 '    UserKnownHostsFile=/dev/null\n'
                 '    StrictHostKeyChecking=no\n'
                 '    CheckHostIP=no\n'
                 '" >> /etc/ssh/ssh_config')

    def _pip_config(self, node_descriptions):
        LOG.warning('Workaround: pip/easy_install configs!')
        mirror = self.pypi_mirror
        for node in node_descriptions.nodes:
            index_url = ''
            if mirror:
                index_url = 'index_url = %s' % mirror
            node.cmd(('cat > ~/.pydistutils.cfg <<<"'
                      '[easy_install]\n'
                      '%s'
                      '"') % index_url)
            node.cmd(('mkdir -p ~/.pip; '
                      'cat > ~/.pip/pip.conf <<<"'
                      '[global]\n'
                      '%s\n'
                      '[install]\n'
                      'use_wheel = false\n'
                      '"') % index_url)

    def _fedora_repo_config(self, node_descriptions):
        """Change the fedora baseurls"""
        mirror = self.fedora_mirror
        for node in node_descriptions.nodes:
            node.cmd("sed -i 's|#baseurl=http://download.fedoraproject.org"
                     "/pub/fedora|baseurl=%s|' "
                     "/etc/yum.repos.d/fedora.repo "
                     "/etc/yum.repos.d/fedora-updates-testing.repo "
                     "/etc/yum.repos.d/fedora-updates.repo" % mirror)
            node.cmd("sed -i 's/metalink=/#metalink=/' "
                     "/etc/yum.repos.d/fedora.repo "
                     "/etc/yum.repos.d/fedora-updates.repo "
                     "/etc/yum.repos.d/fedora-updates-testing.repo")

    def _deregister_rhn(self, node_descriptions):
        """
            Deregister the system from RHN Classic if it's registered.

        """
        LOG.info('Deregistering system from RHN')
        for node in node_descriptions.nodes:
            try:
                node.cmd('rm -rf /etc/sysconfig/rhn/systemid')
            except machine.CommandExecutionError:
                LOG.info('System was not registered with RHN')


class GetNodes(GetNodesBase):
    """
        Create nodes in an Openstack instance.

        Connects to OpenStack and creates some number of VMs. Wait until they
        are accessible with SSH Pass their IPs and other info to other tasks
        in `context['nodes']`. Look at 'common.NodeDescriptions'
        for more info.
    """
    vms = []
    floating_ips = ()
    ostack = None
    reusing_nodes = False  # set to True if existing nodes were found

    def __init__(self, username, password, project, endpoint, image,
                 keypair=None, networks=None, flavor='m1.medium', count=1,
                 node_name='node', reuse=False,
                 explicit_floating_ips=True,
                 config_drive=False, user_data_files=[], **kwargs):
        """
        :param username: user of the OpenStack instance
        :param endpoint: URL to keystone, e.g. 'http://domain.com:5000/v2.0'

        :param image: image or snapshot name from which to boot
        :param keypair: with what keypair should the node be created?
        :param networks: list of networks to which to connect the nodes
        :param flavor: VM flavor that specifies how much resources it gets
        :param count: how many nodes to create

        :param node_name: if `count` is 1, the node will be called like
            this. If more nodes are being created, they will additionally have
            suffixes '-1', '-2', etc.
        :param reuse: if True and nodes with `node_name` + suffixes exist, they
            will be re-used and not created. If the existing nodes aren't in
            the correct state (i.e. in an error state) or if there is different
            number of them than `count`, the task will fail. If `reuse=False`
            and the nodes already exist, it will fail too.
        :param boolean explicit_floating_ips: When set to False we don't try to
            reserve and assign the floating IPs to nodes.
        :param config_drive: Use a virtual cdrom drive as metadata.
        """
        super(GetNodes, self).__init__(**kwargs)
        # auth to the system where we are creating the nodes
        self.username = username
        self.password = password
        self.project = project
        self.endpoint = endpoint

        self.image = image
        self.keypair = keypair
        self.networks = networks
        self.flavor = flavor
        self.count = int(count)
        self.node_name = node_name
        self.reuse = (str(reuse).lower() == 'true')
        self.explicit_floating_ips = (
            str(explicit_floating_ips).lower() == 'true')
        self.config_drive = (str(config_drive).lower() == 'true')
        self.user_data_files = user_data_files

    def run(self, context):
        """
            Create nodes and wait until they are accessible trough SSH.

            It currently gives a floating IP to every node, for simplification.
            A LinuxMachine object pointing to the first node will be in
            "context['nodes'].main_node". For more information, see
            'common.NodeDescriptions'.
        """
        self.ostack = self.connect_openstack()
        names = self.generate_node_names(self.node_name, self.count)
        self.vms = self.ostack.find_existing_nodes(names)
        if self.vms:
            self.reusing_nodes = True
            if not self.reuse:
                raise Exception('Already existing nodes found but reuse not'
                                ' allowed')
            desc = self.reuse_nodes()
        else:
            desc = self.create_nodes(names)
            self._prepare_nodes(desc)

        context['nodes'] = desc
        context['is_inner_stack'] = True

    def cleanup(self, context):
        """
            Delete nodes and release floating IPs.
        """
        if not self.reuse and self.reusing_nodes:
            LOG.info("GetNodes failed because "
                     "reuse=0, skipping node cleanup")
            return

        self.ostack = self.connect_openstack()
        if len(self.vms) == self.count:
            LOG.info('Destroying VMs')
            self.ostack.destroy_nodes(self.vms)
        else:
            # this may be needed if creating VMs partially fails or if `run`
            # wasn't executed
            LOG.info('Destroying VMs by name')
            names = self.generate_node_names(self.node_name, self.count)
            self.ostack.destroy_nodes_by_name(names)

    def reuse_nodes(self):
        """Find existing nodes by what they should be called and use those.

        Doesn't try to get new ones if something is wrong with them
        (inaccessible trough SSH or if some of them are missing).
        """
        wrong_state = [vm.status for vm in self.vms if vm.status != 'ACTIVE']
        if wrong_state:
            raise Exception('Existing nodes found but with wrong state %s',
                            wrong_state)

        desc = self.ostack.get_nodes_description(self.vms)
        LOG.info('Reusing already existing nodes: %s', desc)
        self.floating_ips = set(desc.floating_ips)
        if not self.floating_ips:
            raise Exception("Existing nodes don't have floating IPs")
        desc = create_node_connections(desc, self.ssh_user, self.ssh_pass,
                                       self.ssh_keyfile)
        common.wait_for_ssh(desc.nodes, SSH_TIMEOUT)
        return desc

    def create_nodes(self, names):
        """Create the nodes in OpenStack, try again if it fails.

        At first, the nodes get booted together (to make it faster), but
        everything else (waiting until they are in ACTIVE state, assigning
        floating IPs, waiting until they are accessible trough SSH) is done
        individually.
        """
        result = common.NodeDescriptions([])
        vms = self._boot_nodes(names)
        self.vms = vms[:]
        nodes = []
        while vms:
            vm = vms.pop(0)
            vm = self.ostack.wait_for_active_state(vm)
            if vm.status == 'ERROR':
                self.vms.remove(vm)
                vm = self._retry_node(vm)
                self.vms.append(vm)
            if self.explicit_floating_ips:
                self.ostack.assign_floating_ips([vm])

            desc = self.ostack.get_nodes_description([vm])
            desc = create_node_connections(desc, self.ssh_user,
                                           self.ssh_pass,
                                           self.ssh_keyfile)
            common.wait_for_ssh(desc.nodes, SSH_TIMEOUT)
            result.data += desc.data

        resources_json = open(self.resources_file, 'a')
        for idx, name in enumerate(names):
            if self.metadata is not None:
                nodes.append({'name': name,
                              'ip': result.floating_ips[idx],
                              'private_ip': result.ips[idx],
                              'metadata': self.metadata})
            else:
                nodes.append({'name': name,
                              'ip': result.floating_ips[idx],
                              'private_ip': result.ips[idx]})
        resource_data = [{'nodes': nodes}]
        self.floating_ips = set(result.floating_ips)
        resources = {"resources": resource_data}
        json.dump(resources, resources_json, indent=4)
        resources_json.close()
        LOG.info('Using nodes: %s', result)
        return result

    def connect_openstack(self):
        return nodefactory.NodeFactory(
            auth_url=self.endpoint,
            user=self.username,
            project=self.project,
            pwd=self.password)

    def generate_node_names(self, basename, count):
        """
            Return a list of names for the nodes.
        """
        if count == 1:
            return [basename]
        else:
            return ['%s-%d' % (basename, index) for index in range(1, count+1)]

    def _boot_nodes(self, names):
        """
            Shortcut for starting the node creating
        """
        nodes = []
        if os.path.isfile(WRITE_MIME_MULTI) and len(self.user_data_files) > 0:
            cuuid = str(uuid.uuid1())
            cuser_data_file = '/tmp/combined-user-data-' + cuuid + '.txt'
            user_data = self._combine_cloud_init(cuser_data_file)
        elif len(self.user_data_files) > 0 \
                and not os.path.isfile(WRITE_MIME_MULTI):
            LOG.warning("You provided cloud-init files but to combine them"
                        "you must install the cloud-utils package from EPEL")
            user_data = USER_DATA
        else:
            user_data = USER_DATA
        for name in names:
            node = self.ostack.boot_node(
                name=name,
                image=self.image,
                flavor=self.flavor,
                networks=self.networks,
                keypair=self.keypair,
                config_drive=self.config_drive,
                user_data=user_data)
            nodes.append(node)
        for n in nodes:
            LOG.debug('%s nets: %s' % (n.name, pprint.pformat(n.networks)))
        if os.path.isfile(WRITE_MIME_MULTI) and len(self.user_data_files) > 0:
            rc, out = common.runLocalCmd(['rm', '-f', cuser_data_file])
            LOG.debug('Deleting file %s:\n %s' % (cuser_data_file, out))
        return nodes

    def _retry_node(self, vm):
        """
            Retry booting node a certain number of times
            if in an ERROR state
        """
        retry = 1
        wait = 30
        while retry <= MAX_BOOT_RETRIES:
            total_wait = retry * wait
            LOG.warning("Try '%s' of '%s' failed to provision"
                        % (retry, MAX_BOOT_RETRIES))
            LOG.info("Waiting '%s'" % str(total_wait))
            sleep(total_wait)
            LOG.info("Cleaning up VM in ERROR state")
            self.ostack.destroy_nodes_by_name([vm.name])
            self._boot_nodes([vm.name])
            vm = self.ostack.wait_for_active_state(vm)
            if vm is None:
                raise ("Failed to boot node")
            if vm.status != 'ACTIVE' and vm.status != 'ERROR':
                raise ("Wrong status '%s' of node '%s'"
                       % (vm.status, vm.name))
            if vm.status == "ERROR":
                retry += 1
            if retry == MAX_BOOT_RETRIES:
                msg = "ERROR status of node '%s' on Max retries '%s'" \
                      % (vm.name, MAX_BOOT_RETRIES)
                LOG.error(msg)
                raise (msg)
            if vm.status == 'ACTIVE':
                LOG.info("Status of vm '%s' is ACTIVE" % vm.name)
                break

        return vm

    def _combine_cloud_init(self, cdata_file):
        """
            Combine clout-init user-data files if WRITE_MIME_MULTI tool exits
        """
        self.user_data_files = \
            [THIS_DIR + '/../../{0}'.format(i) for i in self.user_data_files]
        user_data_files = USER_DATA_FILES + self.user_data_files
        rc, out = common.runLocalCmd("%s --output=%s %s"
                                     % (WRITE_MIME_MULTI, cdata_file,
                                        str.join(' ', user_data_files)),
                                     None, None, False, None, False)
        LOG.info('Running %s command:\n %s' % (WRITE_MIME_MULTI, out))
        user_data_file = open(cdata_file, 'r')
        return user_data_file

    def _wait_for_cloud_init(self, node_descriptions):
        """Wait until the cloud init script runs the touch command.
           Normally it should be done by a heat WaitCondition, but we are
           not using heat yet. Without proper waiting we can have connection
           issues.
           TODO: switch to heat.
        """
        test_cmd = '[ -f /cloud_inited ]'
        for node in node_descriptions.nodes:
            retry = 8
            while True:
                try:
                    node.cmd(test_cmd)
                    break
                except machine.CommandExecutionError as ex:
                    retry = retry - 1
                    if retry <= 0:
                        raise ex
                    else:
                        time.sleep(1)


class MockGetNodes(GetNodesBase):
    """ Don't really create the nodes, use existing ones.

    Since GetNodes re-uses nodes if they already exist (recognized by their
    names), this is mostly useful for existing nodes that are not managed by
    OpenStack.

    Used for developing only. It should pass the same `context['nodes']`
    structure as GetNodes and checks for ssh connectivity. Doesn't delete the
    nodes at cleanup.

    You have to set 'existing_nodes' to a list of IPs. The first one will be
    used as the main node.
    """
    def __init__(self, existing_nodes, ssh_wait=SSH_TIMEOUT,
                 ignore_puppet_agent=False, **kwargs):
        """
        :param existing_nodes: list of IPs
        :param ssh_user: user that should connect tho the nodes
        :param ssh_pass: not necessary if `ssh_keyfile` is given
        :param ssh_keyfile: path to the file with the private key of `keypair`,
            not necessary if `ssh_pass` is given
        :param ignore_puppet_agent: when True, do not try to stop and disable
            puppet agent on the machine
        """
        super(MockGetNodes, self).__init__(**kwargs)
        self.ips = existing_nodes
        self.ssh_wait = int(ssh_wait)
        self.ignore_puppet_agent = (str(ignore_puppet_agent).lower() == 'true')

    def run(self, context):
        if not self.ips:
            raise ValueError('No existing_nodes specified!')
        desc = self.connect_ips(self.ips)
        if not self.ignore_puppet_agent:
            self._puppet_unmanage(desc.nodes)
        self._prepare_nodes(desc)
        context['nodes'] = desc

    def cleanup(self, context):
        LOG.info('MockGetNodes - so no cleanup.')

    def connect_ips(self, ips):
        desc = list()
        for ip in ips:
            ip = self._convert_hostname(ip)
            desc.append({"ip": ip, "floating_ip": ip})
        desc = common.NodeDescriptions(desc)
        LOG.info("Using existing nodes: %s", desc)

        desc = create_node_connections(desc, self.ssh_user, self.ssh_pass,
                                       self.ssh_keyfile)
        common.wait_for_ssh(desc.nodes, self.ssh_wait)
        return desc

    def _convert_hostname(self, host):
        info = socket.getaddrinfo(host, None, socket.AF_INET)
        ip = info[0][4][0]
        if ip != host:
            LOG.info('Hostname %s was resolved to %s.' % (host, ip))
        return ip

    def _puppet_unmanage(self, nodes):
        """Make sure machine is not managed by puppet

        This is needed to not interfere with our tasks,
        or at least to not slow them down (yum locks, sshd etc).

        This also tries to run --onetime puppet agent if installed,
        to make sure it has a chance to reach the final state.
        """
        for node in nodes:
            try:
                node.cmd('service puppet stop;'
                         'chkconfig puppet off;'
                         'pkill puppet;'
                         '[[ -f /etc/puppet/puppet.conf '
                         ' && ! -f ~/puppet.conf'
                         ' ]] && ('
                         ' puppet agent --onetime --no-daemonize -t;'
                         ' mv /etc/puppet/puppet.conf ~/;'
                         ' yum reinstall -y puppet )',
                         log_per_line=True,
                         timeout=SSH_TIMEOUT)
            except machine.CommandExecutionError as exc:
                LOG.info('Failures while puppet-unmanaging host: %s', exc)


def create_node_connections(node_descriptions, username, password,
                            ssh_keyfile=None):
    """Create SSH connection for each, return updated node_descriptions.
    """
    if len(node_descriptions.data) != len(node_descriptions.floating_ips):
        # nodes with only internal IPs are currently not supported
        raise Exception("One of the nodes doesn't have a floating IP")

    if ssh_keyfile:
        LOG.info('Going to use ssh keyfile instead of password.')
        password = None
    for node in node_descriptions.data:
        server = machine.LinuxMachine(
            host=node['floating_ip'],
            user=username,
            password=password,
            local=False,
            key_filename=ssh_keyfile)
        server.desc = node
        node['server'] = server
    return node_descriptions