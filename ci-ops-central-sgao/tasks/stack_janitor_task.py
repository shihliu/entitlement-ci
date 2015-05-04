import datetime
import logging
import re
import time

import taskrunner
import nodefactory

LOG = logging.getLogger(__name__)


class StackJanitor(taskrunner.Task):
    """Clean up specified tenant in OpenStack

    Removes old nodes and unassigned floating IPs.
    """
    ostack = None
    _old_nodes = {}
    _free_flips = {}

    def __init__(self, username, password, project, endpoint,
                 older_in_days=1, ignore_pattern='.*permanent.*',
                 flip_delay=60, flip_count=3, remove_vms=True,
                 remove_ips=True, pretend=False, **kwargs):
        """
        :param string username: user of the OpenStack instance
        :param string password: user's password for the OpenStack instance
        :param string project: project/tenant for the OpenStack instance
        :param string endpoint: URL to keystone,
            e.g. 'http://domain.com:5000/v2.0'
        :param number older_in_days: How many days has to pass from the time
            when the node was created to be considered old
        :param string ignore_pattern: if this RegExp pattern matches node
            name, it will not be cleaned up.
        :param number flip_delay: How many seconds to wait between execution
            of additional listing of floating IPs,
            for verification that those found are is still unused.
        :param number flip_count: How many still-unused-FlIP checks to do.
        :param bool remove_vms: if False, skip removing VMs
        :param bool remove_ips: if False, skip removing Floating IPs
        :param bool pretend: if True just print what would be done,
            but do not touch anything
        """
        super(StackJanitor, self).__init__(**kwargs)
        # auth to the system where we are creating the nodes
        self.username = username
        self.password = password
        self.project = project
        self.endpoint = endpoint
        self.older_in_days = datetime.timedelta(days=float(older_in_days))
        self.ignore_pattern = re.compile(ignore_pattern)
        self.flip_delay = float(flip_delay)
        self.flip_count = int(flip_count)
        self.remove_vms = (False if remove_vms == 'False'
                           else bool(remove_vms))
        self.remove_ips = (False if remove_ips == 'False'
                           else bool(remove_ips))
        self.pretend = (False if pretend == 'False' else bool(pretend))

    def run(self, context):
        """Collect old nodes and unused floating IPs."""
        LOG.info('endpoint = %s', self.endpoint)
        LOG.info('username = %s', self.username)
        LOG.info('project = %s', self.project)
        LOG.info('password = %s', self.password)
        LOG.info('older_in_days = %s', self.older_in_days)
        LOG.info('flip_delay = %s', self.flip_delay)
        LOG.info('flip_count = %s', self.flip_count)
        self.ostack = nodefactory.NodeFactory(
            auth_url=self.endpoint,
            user=self.username,
            project=self.project,
            pwd=self.password)

        self.find_old_nodes()
        LOG.info('Nodes to clean:')
        if not self._old_nodes:
            LOG.info('No old nodes found :)')
        for node in self._old_nodes.values():
            LOG.info('%s is %d days and %d hours old\nCreated at %s, ID %s'
                     % (node['srv'].name,
                        node['age'].days, node['age'].seconds / 3600,
                        node['created'], node['srv'].id))

        self.find_free_flips()
        LOG.info('Floating IPs to release:')
        if not self._free_flips:
            LOG.info('No unassigned FlIPs found :)')
        for flip in self._free_flips.values():
            LOG.info('%s is not used (ID %s)'
                     % (flip.ip, flip.id))

    def cleanup(self, context):
        """Delete old nodes and release unused floating IPs."""
        if self.ostack is None:
            self.run(context)

        if self.pretend:
            LOG.info('pretend=True specified so we are done for now')
            return

        nodes_cleaned = len(self._old_nodes)
        flips_freed = len(self._free_flips)

        if self.remove_vms:
            if nodes_cleaned:
                self.ostack.destroy_nodes(
                    [node['srv'] for node in self._old_nodes.values()],
                    check_state=False)
            else:
                LOG.info('No nodes to clean.')
        else:
            LOG.info('VM Removal disabled.  Old VMs were not removed.')
            nodes_cleaned = 0

        if self.remove_ips:
            if flips_freed:
                self.ostack.release_floating_ips(
                    [flip.ip for flip in self._free_flips.values()])
            else:
                LOG.info('No unassigned floating IPs to clean.')
        else:
            LOG.info('Floating IP Removal disabled. '
                     'Unused Floating IPs were not removed.')
            flips_freed = 0

        LOG.info('Build mark: cleaned=%dvm-%dip'
                 % (nodes_cleaned, flips_freed))

    def find_old_nodes(self):
        LOG.info('Searching for old nodes ...')
        servers = self.ostack.nova.servers.list()
        now = datetime.datetime.utcnow()
        min_birthday = now - self.older_in_days
        for srv in servers:
            # atm we support only static 'Z'
            # character at the end, denoting UTC
            if self.ignore_pattern.match(srv.name):
                continue
            created = datetime.datetime.strptime(
                srv.created,
                '%Y-%m-%dT%H:%M:%SZ')
            if created < min_birthday:
                self._old_nodes[srv.id] = {
                    'srv': srv,
                    'created': created,
                    'age': (now - created)}

    def find_free_flips(self):
        free = self._find_free_flips()
        LOG.info('Found %d unassigned floating IPs in first check'
                 % len(free))

        if len(free) == 0:
            return

        run_count = 1

        while run_count < self.flip_count:
            run_count += 1

            LOG.info('Waiting %d seconds before recheck ...' % self.flip_delay)
            time.sleep(self.flip_delay)

            still_free = self._find_free_flips().keys()
            LOG.info('Found %d unassigned floating IPs in %d. check'
                     % (len(still_free), run_count))

            for flip in free.values():
                if flip.id not in still_free:
                    LOG.info('FlIP %s is assigned after %d check'
                             % (flip.ip, run_count))
                    free.pop(flip.id)

        self._free_flips = free

    def _find_free_flips(self):
        LOG.info('Searching for unassigned floating IPs ...')
        free = {}
        flips = self.ostack.nova.floating_ips.list()
        for flip in flips:
            if flip.fixed_ip is None and flip.instance_id is None:
                free[flip.id] = flip
        return free
