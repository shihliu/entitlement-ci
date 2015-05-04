import logging
import pprint
import urlparse
import os
from random import randint
from time import sleep

from keystoneclient.v2_0 import client as keystone
from novaclient import client as nova
from novaclient import exceptions as nova_exc
from glanceclient import client as glance

from tasks import common

JENKINS_HOME = os.environ.get('JENKINS_HOME', '')
JOB_NAME = os.environ.get('JOB_NAME', '')
BUILD_NUMBER = os.environ.get('BUILD_NUMBER', '')

LOG = logging.getLogger(__name__)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(
    logging.WARNING)

TIMEOUT_BUILD = 20 * 60
TIMEOUT_DELETED = 4 * 60
MAX_WAIT_TIME = 100
MAX_ATTEMPTS = 90


class NodeFactory(object):
    def __init__(self, auth_url, user, project, pwd):
        self.creds = {'auth_url': auth_url,
                      'user': user,
                      'pass': pwd,
                      'tenant': project}
        host = urlparse.urlsplit(auth_url).hostname
        LOG.info(('Using OpenStack controller '
                  'http://{0}/dashboard/project/instances/').format(host))
        self._connect_keystone(self.creds)
        self._connect_nova(self.creds)
        self._connect_glance(self.creds)

    def boot_node(self, name, image, flavor, networks=None, keypair=None,
                  user_data=None, **kwargs):
        """Starts booting a node, but doesn't wait until it's in ACTIVE state.
        """
        LOG.debug('Creating node %s', name)
        if networks is None:
            networks = []
        LOG.info("Checking if image, flavor, and network exist")
        self.image_id(image)
        self.flavor_id(flavor)
        [self.network_id(net_name) for net_name in networks]
        LOG.info('Booting node %s using image %s and flavor %s'
                 % (name, image, flavor))
        attempts = 1
        # Added in code to try to boot a resource for a random time
        # between 10 and MAX_WAIT_TIME in seconds (set at the top)
        # try for MAX_ATTEMPTS (set at the top)
        while attempts <= MAX_ATTEMPTS:
            try:
                node = self.nova.servers.create(
                    name=name,
                    key_name=keypair,
                    image=self.image_id(image),
                    flavor=self.flavor_id(flavor),
                    nics=[{'net-id': self.network_id(net_name)}
                          for net_name
                          in networks],
                    userdata=user_data,
                    **kwargs)

                self.log_node_info(node, LOG.info)
                return node
            except nova.exceptions.OverLimit:
                LOG.info("Still not enough quota available for %s", name)
                wait_time = randint(10, MAX_WAIT_TIME)
                LOG.info("Attempt %s of %s waiting for %s seconds"
                         % (attempts, MAX_ATTEMPTS, wait_time))
                sleep(wait_time)
                if (attempts == MAX_ATTEMPTS):
                    LOG.info("QUOTA NOT AVAILABLE for %s", name)
                    if JENKINS_HOME and JOB_NAME and BUILD_NUMBER:
                        file_dir = \
                            JENKINS_HOME + '/jobs/' + JOB_NAME +    \
                            '/builds/' + BUILD_NUMBER
                        file_path = os.path.join(file_dir, 'quotaFailure')
                        common.touch(file_path)
                        raise NodeStatusError("Failed to boot node: "
                                              "Quota not available for %s" %
                                              name)
                attempts += 1

    def wait_for_active_state(self, node):
        node = self._wait_till_node_not_building(node)
        if node is None:
            raise NodeStatusError("Failed to boot node")
        if node.status != 'ACTIVE' and node.status != 'ERROR':
            raise NodeStatusError("Wrong status '%s' of node '%s'"
                                  % (node.status, node.name))
        return node

    def find_existing_nodes(self, names):
        """ Find existing VMs by name
        """
        nodes = [self.get_node(name) for name in names]
        nodes = filter(None, nodes)
        if len(nodes) == 0:
            return []
        elif len(nodes) != len(names):
            # found only some of the nodes
            found = [node.name for node in nodes]
            missing = list(set(names) - set(found))
            raise NodesNotFound(missing, found)
        LOG.info('Found existing nodes:')
        for node in nodes:
            self.log_node_info(node, LOG.info)
        return nodes

    def destroy_nodes_by_name(self, names):
        """ Find nodes by how they should be named and delete them.

        Used when creating nodes partially failed.
        """
        nodes = [self.get_node(name) for name in names]
        nodes = filter(None, nodes)
        self.destroy_nodes(nodes)

    def destroy_nodes(self, nodes, check_state=True):
        LOG.info('Node deletion requested ...')
        if not nodes:
            LOG.error('Nothing to stop - nodes(s) not found!')
            return
        LOG.info('Found and deleting nodes:')
        ips = []
        removed = []

        # get fresh info for vms (needed for state matching)
        existing = self.nova.servers.list()
        nodes_id = [node.id for node in nodes]
        nodes = [node for node in existing if node.id in nodes_id]

        for node in nodes:
            if check_state and node.status not in ('ACTIVE', 'ERROR'):
                LOG.error('Unable to delete due to wrong state:')
                self.log_node_info(node, LOG.error)
                continue
            self.log_node_info(node, LOG.info)
            ips.append(self.node_floating_ip(node, in_list_only=True))
            try:
                node.delete()
                removed.append(node.name)
            except Exception:
                LOG.exception('Proceeding after node.delete() failure!')
        try:
            self._wait_till_nodes_deleted(removed)
        except common.TimeoutError:
            LOG.exception('Proceeding after node deletion'
                          'timedout.')
        self.release_floating_ips(filter(None, ips))

    def assign_floating_ips(self, nodes):
        pool = self.nova.floating_ip_pools.list()[0]
        LOG.debug('Using IP pool named %s', pool.name)
        ips = []
        float_ip = None
        for node in nodes:
            try:
                float_ip = self.nova.floating_ips.create(pool=pool.name)
                LOG.debug('Adding IP %s', float_ip.ip)
                node.add_floating_ip(float_ip)
                ips.append(float_ip.ip)
            except Exception as ex:
                if float_ip is not None:
                    LOG.error('Attachment of floating IP failed: %s' % ex)
                    self.release_floating_ips((float_ip,))
                else:
                    LOG.error('Floating IP creation failed: %s' % ex)
                raise
        return ips

    def release_floating_ips(self, ips):
        ip_objects = dict([(ip.ip, ip.id) for ip
                           in self.nova.floating_ips.list()])
        ips = filter(lambda ip: ip in ip_objects, ips)
        if not ips:
            LOG.info('No floating IP to release found.')
            return
        for ip in ips:
            try:
                LOG.info('Releasing Floating IP %s' % ip)
                self.nova.floating_ips.delete(ip_objects[ip])
                LOG.info('Floating IP %s released' % ip)
            except Exception:
                LOG.exception('Proceeding after floating_ip delete() '
                              'failure!')

    def get_node(self, name):
        nodes = self.nova.servers.list()
        for node in nodes:
            n = getattr(node, 'name', None)
            if n == name:
                return node
        return None

    def get_nodes_description(self, nodes):
        desc = list()
        for node in nodes:
            d = dict()
            d["ip"] = self.node_ip(node)
            d["floating_ip"] = self.node_floating_ip(node)
            desc.append(d)
        return common.NodeDescriptions(desc)

    def image_id(self, image_name_or_id):
        """Find Image ID in Glance for provided name or ID.

        If specified image name or ID does not exists raises ObjectNotFound.
        """
        images = list(self.glance.images.list())
        img = [im_ for im_ in images if im_.id == image_name_or_id]
        img = img or [im_ for im_ in images if im_.name == image_name_or_id]
        if not img:
            raise ObjectNotFound('Image', image_name_or_id)
        img = img[0]
        LOG.info('Found image %s (%s).', img.name, img.id)
        return img

    def network_id(self, network_name):
        try:
            return self.nova.networks.find(
                label=network_name).id
        except nova_exc.NotFound:
            raise ObjectNotFound('Network', network_name)

    def flavor_id(self, flavor_name):
        try:
            return self.nova.flavors.find(
                name=flavor_name).id
        except nova_exc.NotFound:
            raise ObjectNotFound('Flavor', flavor_name)

    def node_ip(self, node, network=None):
        if network is None:
            network = node.networks.keys()[0]
        return node.networks[network][0]

    def node_floating_ip(self, node, in_list_only=False):
        ip_objects = dict((ip.instance_id, ip.ip) for ip
                          in self.nova.floating_ips.list())
        if node.id in ip_objects:
            return ip_objects[node.id]
        else:
            if not in_list_only and len(node.networks):
                # if there is no FlIP for this node in
                # nova floating list, it's still possible
                # that machine got address automatically
                # so we do pick the last ip from the first network
                net = node.networks.keys()[0]
                if len(node.networks[net]):
                    return node.networks[net][-1]
            return None

    def log_node_info(self, node, logger=None):
        if logger is None:
            logger = LOG.info
        if node is None:
            logger('node == None')
            return

        extra = []
        hyperv = getattr(node, 'OS-EXT-SRV-ATTR:hypervisor_hostname', None)
        host = getattr(node, 'OS-EXT-SRV-ATTR:host', hyperv)
        instance_id = getattr(node, 'OS-EXT-SRV-ATTR:instance_name', None)

        extra.append(node.id)  # uuid
        if instance_id is not None:
            # hypervisor id
            extra.append('instance_id:'+instance_id)
        if host is not None:
            extra.append('host:'+host)
        if host != hyperv and hyperv is not None:
            extra.append('hyperv:'+hyperv)

        task_state = getattr(node, 'OS-EXT-STS:task_state', None)

        logger('{name} - {status}/{task_state} - created {created}'
               ' - {networks} - {extra}'.format(
                   name=node.name,
                   status=node.status,
                   task_state=task_state,
                   created=node.created,
                   networks=','.join([','.join(node.networks[net])
                                      for net in node.networks]),
                   extra=' '.join(extra),
               ))

    def log_debug_status(self):
        LOG.debug('=============== START OF DEBUG =====')
        flavors = self.nova.flavors.list()
        nodes = self.nova.servers.list()
        imgs = self.glance.images.list()

        LOG.debug('==== Flavors: ====')
        LOG.debug(pprint.pformat(flavors))
        LOG.debug('==== Servers: ====')
        for node in nodes:
            self.log_node_info(node, LOG.debug)
        LOG.debug('==== Images: ====')
        for img in imgs:
            LOG.debug(pprint.pformat(img))
        LOG.debug('================= END OF DEBUG =====')

    def _wait_till_node_not_building(self, node):
        return common.wait_for(
            ('Waiting for end of BUILD state of %s' % node.name),
            lambda node: node.status != 'BUILD',
            lambda: self.get_node(node.name),
            timeout_sec=TIMEOUT_BUILD)

    def _wait_till_nodes_deleted(self, node_names):
        return common.wait_for(
            'Wait until end of deletion',
            lambda nodes: not any([node for node in nodes if node.name in
                                   node_names]),
            lambda: self.nova.servers.list(),
            timeout_sec=TIMEOUT_DELETED)

    def _connect_keystone(self, creds):
        try:
            self.keystone = keystone.Client(
                username=creds['user'],
                password=creds['pass'],
                tenant_name=creds['tenant'],
                auth_url=creds['auth_url'])
        except Exception:
            LOG.error('Keystone connection failed with creds: %s'
                      % creds)
            raise
        self.creds['token'] = self.keystone.auth_token
        LOG.debug('Keystone connected with tokens first 32 chars: %s',
                  self.creds['token'][0:32])

    def _connect_nova(self, creds):
        self.nova = nova.Client(
            '1.1',
            creds['user'],
            creds['pass'],
            creds['tenant'],
            auth_url=creds['auth_url'],
            service_type='compute')
        LOG.debug('Nova connected')

    def _connect_glance(self, creds):
        glance_url = self.keystone.service_catalog.url_for(
            service_type='image',
            endpoint_type='publicURL')
        self.glance = glance.Client('1', glance_url, token=creds['token'])
        LOG.debug('Glance %s connected' % glance_url)


class NodeStatusError(Exception):
    def __init__(self, reason):
        super(NodeStatusError, self).__init__(
            'Node preparation failed: %s' % reason)


class ObjectNotFound(Exception):
    """ Used for OpenStack objects, e.g. images, networks, etc. """
    def __init__(self, obj_type, key):
        super(ObjectNotFound, self).__init__(
            '%s %s not found' % (obj_type, key))


class NodesNotFound(Exception):
    def __init__(self, missing, found=None):
        super(NodesNotFound, self).__init__(
            'Only a part of the nodes were found. Nodes %s not found while %s \
            exists' % (missing, found))
