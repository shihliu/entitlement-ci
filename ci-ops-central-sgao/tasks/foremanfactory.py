# This task works under the assumption that a valid foreman server is up and
# running with the foreman_reserve plugin installed
# (https://github.com/david-caro/foreman_reserve/)
# and the python_foreman library is installed/can be accessed as well
# (https://github.com/david-caro/python_foreman/)

import datetime
import logging
import shlex
import subprocess

import requests
import json

from tasks import common
from tasks import get_nodes_task
from foreman import client as foreman_client

# pylint: disable=E1103

LOG = logging.getLogger(__name__)


PUMA_SPEED = 10000
IF_SPEED = 1000


class GetForemanNodesTask(get_nodes_task.MockGetNodes):
    """Get and/or prepare baremetal nodes from foreman.

    Connects to Foreman, if needed acquire a fixed amount of physical machines,
    or use the ones explicitely provided.
    Rebuild/reprovision the machines with specified Operating System
    and create ssh connection to them for other tasks (as context['nodes']).

    This task is expected to be used in following use-cases:

    A) fully automated jobs:
        * auto-select machines
        * reserve them
        * reprovision
        * pass to other tasks (context)
        * release at cleanup
    B) manually triggered jobs:
        * use existing nodes (specified in job, maybe as parameter)
        * reserve them
        * reprovision
        * pass to context
        * release at cleanup
    C) manually from command line:
        * use existing nodes (provided by user)
        * optionally reprovision
        * pass to context

    For A and B specify reserve=True.
    For A specify count and (hostgroup and/or prefix).
    For B and C specify existing_nodes.
    For reprovisioning use rebuild=True and specify distribution.
    """
    # How long to wait before 'build' flag
    # on foreman changes from true to false
    _build_flag_timeout = 30*60
    _api_version = 2

    _rest_response_ok = 200
    # Add these API pathes to fetch data through Katello API, which
    # is not supported by `python-foreman`.
    # Read more here:
    # https://github.com/david-caro/python-foreman/issues/25
    _get_api_path_to_systems = 'api/v2/systems'
    _get_api_path_to_organizations = 'api/v2/organizations'
    _get_api_path_to_content_view_fmt = '/'.join(['api/v2/organizations',
                                                  '{id}/content_views'])

    def __init__(self, foreman_url, username, password,
                 foreman_version=None,
                 existing_nodes=None,
                 provisioning_timeout=None,
                 reserve=False, reserve_message=None, count=1,
                 wait_for_reservation=0,
                 hostgroup=None, prefix=None,
                 rebuild=True, distribution='',
                 distribution_id=None,
                 ptable=None, ptable_id=None,
                 media=None, medium_id=None,
                 os_mapping=None,
                 is_satellite=False,
                 location=None,
                 organization=None,
                 lifecycle=None,
                 **kwargs):
        """
        :param foreman_url: http url specified which foreman to use
        :param username: credentials for foreman
        :param password: credentials for foreman
        :param foreman_version: foreman_version of the foreman client to use
        :param existing_nodes: list of machine hostnames (optional),
            use it if you want to explicitely define which machines to use
        :param provisioning_timeout: how long (sec) to wait for machine to
            finish rebuild
        :param reserve: if the machines should be marked as reserved
            with foreman_reserve plugin
        :param reserve_message: marker text which will be used as
            reservation notice together with 'rhos-qe-jenkins' mark
            and current datetime in utc
        :param count: how many machines should be automatically selected
            via reservation
        :param wait_for_reservation: how many minutes(!) wait for machines
            available for reservation (0=don't wait)
        :param hostgroup: name of hostgroup from which the auto-selection
            can pick the machines
        :param prefix: hostname prefix, similar to the hostgroup, this
            can be used to limit from which machines the auto-selection
            may pick
        :param rebuild: if the machine should be reprovisioned before
            passing them forward to other tasks
        :param distribution: keyword for Operating System or Content View
            which should be used when machines are reprovisioned.
            When empty string is provided OS is not changed.
        :param is_satellite: flag to determine if content view is used
            instead of installation media.
        :param location: the location of the machine
        :param organization: the organization that is associated with
            the machine
        :param lifecycle: the content view's life-cycle
            (used only in satellite)

        Extra arguments may be passed, like ssh_user/ssh_keyfile etc,
        see tasks.get_nodes_task.MockGetNodes for details.
        """

        super(GetForemanNodesTask, self).__init__(
            existing_nodes=existing_nodes, **kwargs)
        self.foreman_url = foreman_url
        self.username = username
        self.password = password
        self.foreman_version = foreman_version
        self.provisioning_timeout = int(provisioning_timeout) if \
            provisioning_timeout else self._build_flag_timeout
        self.hostnames = existing_nodes
        self.reserve = str(reserve).lower() == 'true'
        self.reserve_message = 'rhos-qe-jenkins for %s at %s' % (
            reserve_message, datetime.datetime.utcnow())
        self.count = int(count)
        self.wait_for_reservation = int(wait_for_reservation) * 60
        self.hostgroup = hostgroup
        self.prefix = prefix
        self.rebuild = str(rebuild).lower() == 'true'
        self.distribution = distribution
        self.os_mapping = os_mapping

        self.hosts = []
        self.foreman = None

        if not any([self.hostnames, self.hostgroup, self.prefix]):
            raise ValueError(
                'Machine names, hostgroup or prefix has to be provided.')

        if self.hostnames and any([self.hostgroup, self.prefix]):
            raise ValueError('Mixing of existing_nodes and'
                             ' hostgroup|prefix based reservation'
                             ' is not implemented!')

        if any([self.hostgroup, self.prefix]):
            if not self.reserve:
                LOG.warning("Overriding reserve to True - "
                            "Hostgroup or prefix can be used only "
                            "together with reservation.")
            self.reserve = True
            if self.count < 1:
                raise ValueError('Hostgroup or prefix require that count'
                                 ' is set to at least 1.')

        if self.hostnames and self.count != len(self.hostnames):
            LOG.warning("Going to reserve explicitely specified nodes "
                        "so overriding count from %d to %d",
                        self.count, len(self.hostnames))
            self.count = len(self.hostnames)

        self.distribution_id = distribution_id
        self.ptable = ptable
        self.ptable_id = ptable_id
        self.media = media
        self.medium_id = medium_id
        self.is_satellite = is_satellite
        self.location = location
        self.organization = organization
        self.lifecycle = lifecycle

    def connect(self):
        return foreman_client.Foreman(
            url=self.foreman_url,
            auth=(self.username, self.password),
            version=self.foreman_version,
            api_version=self._api_version)

    def run(self, context):
        """Obtain and prepare the machines."""
        self.foreman = self.connect()

        if self.reserve:
            if self.wait_for_reservation:
                self.hosts = self.reserve_hosts_or_wait()
            else:
                self.hosts = self.reserve_hosts()
        else:
            self.hosts = self.find_hosts()

        if not self.hosts or len(self.hosts) != self.count:
            raise Exception('Failed to find or reserve machines!')

        if self.rebuild:
            self.rebuild_hosts()

        # override IPs for MockGetNodes
        # whatever if they are for already known 'existing_nodes'
        # or just reserved machines
        self.ips = []
        for host in self.hosts:
            self.ips.append(host['ip'])

    def cleanup(self, context):
        """Release machines which were reserved by this task."""
        if self.reserve:
            if not self.foreman:
                self.foreman = self.connect()
            self.release_hosts()
            self.show_reserved()

    def rebuild_hosts(self):
        LOG.info('rebuilding all hosts')
        host_props = {'build': True}
        if self.distribution:
            if self.is_satellite:
                content_view_dict = self.get_content_view_dict()
                host_props.update(content_view_dict['os'])
            else:
                host_props.update(self.get_os_dict())
        for host in self.hosts:
            LOG.info('rebuilding host {hostname}\nwith dict: {dict}'.
                     format(hostname=host['name'], dict=host_props))
            if self.is_satellite and \
                    not self.update_system(host, content_view_dict['system']):
                raise ValueError('Could not set to %s the desired '
                                 'content view id' % host['name'])

            if not self.update_host(host['id'], host_props):
                raise ValueError('Could not set %s into build mode'
                                 % host['name'])
            LOG.info("host status: {dict}".
                     format(dict=self.foreman.show_hosts(host['name'])))
            self._reboot_host(host)
        common.wait_for(
            'wait for reprovisioning',
            lambda hosts: not any([host['build'] for host in hosts]),
            lambda: self.find_hosts(),
            timeout_sec=self.provisioning_timeout,
            wait_sec=20)

    def update_host(self, host_id, params):
        """
        Description: update host in foreman system
        :param host_id: host id in foreman
        :param params: dictionary with parameters to update
        @return True if host is updated successfully, False otherwise
        """
        self.foreman.update_hosts(host_id, params)
        hostname = self.foreman.show_hosts(host_id)['name']
        updated_host = self.foreman.show_hosts(host_id)
        # TODO(bshuster): use `_get_update_diff` instead
        check_diff = filter(lambda x: updated_host[x] != params[x], params)
        if check_diff:
            expected = dict((i, params[i]) for i in check_diff)
            actual = dict((i, updated_host[i]) for i in check_diff)
            LOG.error("Update failed\nExpected settings: %s"
                      "\nActual settings: %s", expected, actual)
            return False

        LOG.info("Host '%s' was updated successfully "
                 "with next parameters %s", hostname,
                 ', '.join(['%s=%s' % (key, val) for key,
                           val in params.iteritems()]))
        return True

    def _get_update_diff(self, req_params, res_params):
        """
        Description: check the differences between two dictionaries
            and return them as a dictionary.
            The dictionary looks like this:
                {
                    'expected': {'param1': 'val1',
                                 'param2': 'val2'},
                    'actual': {'param1': 'val22',
                               'param2': 'val213'}
                }
        :param req_param: the request parameters dictionary
        :param res_param: the response parameters dictionary
        """
        diff_list = filter(lambda x: res_params[x] != req_params[x],
                           req_params)
        expected = None
        actual = None
        if diff_list:
            expected = dict((i, req_params[i]) for i in diff_list)
            actual = dict((i, res_params[i]) for i in diff_list)
        return dict(expected=expected, actual=actual)

    def _get_system_uuid(self, hostname):
        """
        Description: get the uuid of the system that is associated with a given
            hostname
        :param hostname: the given hostname
        @return the system uuid
        """
        org_id = self._get_organization_id()
        params = {'search': 'name="{}"'.format(hostname)}

        system_uuids_hash = self._katello_get_request('/'.join([
            self._get_api_path_to_organizations, str(org_id), 'systems']),
            params)
        not_found_msg = 'Could not find system uuid of %s' % hostname
        multiple_msg = ' '.join(['Something is wrong in Satellite;',
                                 'Multiple system uuids were found for',
                                 hostname])
        self._check_valid_response(system_uuids_hash, not_found_msg,
                                   multiple_msg)

        return system_uuids_hash[0]['uuid']

    def update_system(self, host, params):
        """
        Description: update the system that is associated with a given
            host with the given parameters.
        :params host: a dictionary of the host parameters
        :param params: dictionary of the host new parameters
        @return True if update succeeded, otherwise False
        """
        system_uuid = self._get_system_uuid(host['name'])

        # This is a hack; Right now, `python-foreman` doesn't get the Katello
        # apidoc. I am using `requests` to send a PUT REST request to Katello
        # that updates the system with the given parameters.
        response = requests.put('/'.join([self.foreman_url, 'katello',
                                          self._get_api_path_to_systems,
                                          str(system_uuid)]),
                                verify=False,
                                auth=(self.username, self.password),
                                data=json.dumps(params),
                                headers={'content-type': 'application/json'})
        if response.status_code != self._rest_response_ok:
            raise Exception('Update request failed %s' % response.text)
        updated_system_hash = response.json()
        diff_hash = self._get_update_diff(params, updated_system_hash)
        if diff_hash['expected']:
            LOG.error("Update failed\nExpected settings: %s"
                      "\nActual settings: %s", diff_hash['expected'],
                      diff_hash['actual'])
            return False

        LOG.info("Host '%s' was updated successfully "
                 "with next parameters %s", host['name'],
                 ', '.join(['%s=%s' % (key, val) for key,
                            val in params.iteritems()]))
        return True

    def _katello_get_request(self, api_path, params):
        """
        Description: `python-foreman` doesn't get Katello apidoc.
            I have written this method to send GET REST requests
            to Katello API till issue #25 will be resolved:
            https://github.com/david-caro/python-foreman/issues/25
        """
        katello_api_path = '/katello/' + api_path
        req_headers = {'content-type': 'application/json'}

        response = requests.get(self.foreman_url + katello_api_path,
                                auth=(self.username, self.password),
                                verify=False,
                                data=json.dumps(params),
                                headers=req_headers)
        if response.status_code == self._rest_response_ok\
                and 'results' in response.json():
            return response.json()['results']
        raise Exception('Katello request failed:\n'
                        'Response:%s\n'
                        'API Path:%s\n' % (response.text, katello_api_path))

    def _check_valid_response(self, data, not_found_msg, multiple_msg):
        """
        Description: test if a given response has only
            one result. If not, the a appropriate message is displayed
        :param data: the response's results
        :param not_found_msg: the displayed message if there are no results
        :param multiple_msg: the displayed message if there are more than one
            result
        """
        assert len(data), ('%s' % not_found_msg)
        assert len(data) == 1, ('%s' % multiple_msg)

    def _get_organization_id(self):
        """
        @return the organization id
        """
        params = {'search': 'name={}'.format(self.organization)}
        organizations_hash = self._katello_get_request(
            self._get_api_path_to_organizations,
            params)
        not_found_msg = ' '.join(['Organization', self.organization,
                                  'not found in', 'Satellite'])
        multiple_msg = ' '.join(['Something wrong with Satellite;',
                                 'Found multiple organizations that',
                                 'have the same name', self.organization])
        self._check_valid_response(organizations_hash, not_found_msg,
                                   multiple_msg)
        return organizations_hash[0]['id']

    def _get_content_view_id(self):
        """
        @return the content view id according to the `distribution`
        """
        params = {'search': 'name="{}"'.format(self.distribution)}
        org_id = self._get_organization_id()
        content_views_hash = self._katello_get_request(
            self._get_api_path_to_content_view_fmt.format(id=org_id), params)
        not_found_msg = ' '.join(['Content view', self.distribution,
                                  'was not found', 'in Satellite'])
        multiple_msg = ' '.join(['Something wrong with Satellite;',
                                 'Found multiple content views that',
                                 'have the same name', self.distribution])
        self._check_valid_response(content_views_hash, not_found_msg,
                                   multiple_msg)

        return content_views_hash[0]['id']

    def _set_ptable(self, content_view_map):
        if not self.ptable_id:
            if not self.ptable:
                self.ptable = content_view_map['ptable']
        ptable_list = self.foreman.index_ptables(
            search='{name}'.format(name=self.ptable))['results']
        ptable_not_found_msg = ' '.join(['Distribution', self.ptable,
                                         'not found in Satellite'])
        ptable_multiple_msg = ' '.join(['Something is wrong in Satellite;',
                                        'Multiple matches for ptable',
                                        self.ptable, 'found in Satellite:\n',
                                        str('\n'.join(str(o)
                                                      for o in ptable_list))])

        self._check_valid_response(ptable_list, ptable_not_found_msg,
                                   ptable_multiple_msg)
        self.ptable_id = ptable_list[0]['id']

    def _set_medium(self, content_view_map):
        if not self.medium_id:
            if not self.media:
                organization_name = self.organization
                self.media = '/'.join([organization_name,
                                       'Library',
                                       content_view_map['media']])
            media_list = filter(
                lambda m: m['name'] == self.media,
                self.foreman.index_media(search='{name}'.
                                         format(name=self.media))['results'])
            media_not_found_msg = ' '.join(['Medium', self.media,
                                            'not found in Satellite'])
            media_multiple_msg = ' '.join(['Something is wrong in Satellite;',
                                           'Multiple matches for media',
                                           self.media, 'found in Satellite\n',
                                           str('\n'.join(str(o)
                                                         for o in media_list))
                                           ])
            self._check_valid_response(media_list, media_not_found_msg,
                                       media_multiple_msg)
            self.medium_id = media_list[0]['id']

    def _get_operating_system_id(self):
        os_id = None
        for os_ix in self.foreman.operatingsystems.index()['results']:
            os_ = self.foreman.operatingsystems.show(os_ix['id'])
            for media in os_['media']:
                if media['name'] == self.media:
                    os_id = os_ix['id']
                    break
        return os_id

    def _get_environment_id(self, katello_env_name):
        # This is a hack:
        # In Satellite, any Foreman environment is associated with only one
        # Katello environment (organization, lifecycle, content view) and
        # vice versa. In other words, Foreman environment names are
        # named in the following way:
        # KT_<Organization_name>_<LifeCycle_name>_<ContentView_name>_
        # <ContentView_id>
        # we will use this pattern in order to get the environment id.
        env_id = None
        for foreman_env in self.foreman.environments.index()['results']:
            if foreman_env['name'] == katello_env_name:
                env_id = foreman_env['id']
                break
        return env_id

    def get_content_view_dict(self):
        """
        @return dict: dictionary of required values for updating the host and
             the system related to that host.
             The dictionary has:
                 content_view_id=self.distribution_id
                 ptable_id=self.ptable_id,
                 medium_id=self.medium_id
                 operatingsystem_id,
                 environment_id
        """
        content_view_name = self.distribution
        self.distribution_id = self._get_content_view_id()

        # This part is required due to a bug #xyzwe in Satellite API:
        # The `system` is a relation  between the `host` in Foreman and
        # the `content view` in Katello. When a system is updated with a new
        # content view, the host's environment, operating system and media
        # have to be updated as well but unfortunately, this doesn't happen
        # in Satellite. Therefore, it's our job to do that.

        if not self.ptable or not self.medium_id:
            update_dict = self.os_mapping[content_view_name]

        self._set_ptable(update_dict)
        self._set_medium(update_dict)

        os_id = self._get_operating_system_id()
        assert(os_id), ('No operating system associate with %s media in'
                        'Satellite' % self.media)

        katello_env_name = '_'.join(['KT', self.organization, self.lifecycle,
                                     self.distribution,
                                     str(self.distribution_id)])
        env_id = self._get_environment_id(katello_env_name)
        assert(env_id), ('Environment %s was not found in Satellite' %
                         katello_env_name)

        return dict(system=dict(content_view_id=self.distribution_id),
                    os=dict(operatingsystem_id=os_id,
                            ptable_id=self.ptable_id,
                            environment_id=env_id,
                            medium_id=self.medium_id))

    def get_os_dict(self):
        """
        @return dict: dictionary of values needed for host_update
            operatingsystem_id=self.distribution_id,
            ptable_id=self.ptable_id,
            medium_id=self.medium_id
        """
        if not self.distribution_id:
            os_name, os_version = self.distribution.split('-', 1)
            # in foreman, rhel -> RedHat
            os_name = "RedHat" if os_name == "rhel" else os_name
            major, minor = os_version.split('.', 1)
            os_list = self.foreman.index_operatingsystems(
                search='name = {name} and major = {mj} and minor = {mn}'.
                format(name=os_name, mj=major, mn=minor))['results']
            assert len(os_list), ('Distribution %s not found in foreman' %
                                  self.distribution)
            if len(os_list) > 1:
                print_list = '\n'.join(str(o) for o in os_list)
                LOG.warning("Multiple matches for distribution %s found "
                            "in foreman, choosing the 1st",
                            self.distribution, str(print_list))

            self.distribution_id = os_list[0]['id']
        else:
            os_dict = self.foreman.show_operatingsystems(
                self.distribution_id)['operatingsystem']
            os_name = os_dict['name']
            major = os_dict['major']

        os_key = '-'.join([os_name, major]) if os_name == "RedHat" else os_name

        if not self.ptable_id:
            if not self.ptable:
                update_dict = self.os_mapping[os_key]
                self.ptable = update_dict['ptable']

            ptable_list = self.foreman.index_ptables(
                search='{name}'.format(name=self.ptable))['results']
            assert len(ptable_list), ('Distribution %s not found in foreman' %
                                      self.ptable)
            if len(ptable_list) > 1:
                print_list = '\n'.join(str(o) for o in ptable_list)
                LOG.warning("Multiple matches for ptable %s found "
                            "in foreman, choosing the 1st",
                            self.ptable, str(print_list))
            self.ptable_id = ptable_list[0]['id']

        if not self.medium_id:
            if not self.media:
                update_dict = self.os_mapping[os_key]
                self.media = update_dict['media']

            # require extra filtering as media might have
            # multiple matches (Fedora, FedoraX)
            media_list = filter(
                lambda m: m['name'] == self.media,
                self.foreman.index_media(search='{name}'.
                                         format(name=self.media))['results'])
            assert len(media_list), ('Medium %s not found in foreman' %
                                     self.media)
            if len(media_list) > 1:
                print_list = '\n'.join(str(o) for o in media_list)
                LOG.warning("Multiple matches for medium %s found "
                            "in foreman, choosing the 1st",
                            self.ptable, str(print_list))
            self.medium_id = media_list[0]['id']

        host_dict = dict(operatingsystem_id=self.distribution_id,
                         ptable_id=self.ptable_id,
                         medium_id=self.medium_id)
        LOG.info('Update hosts with dict %s' % host_dict)
        return dict(operatingsystem_id=self.distribution_id,
                    ptable_id=self.ptable_id,
                    medium_id=self.medium_id)

    def find_hosts(self):
        return [self.foreman.show_hosts(h) for h in self.hostnames]

    def release_hosts(self):
        if not self.hosts:
            LOG.error('We should release some hosts but we have none!')
            return
        query_hosts = []
        for host in self.hosts:
            query_hosts.append('name = %s' % host['name'])
        query = ' or '.join(query_hosts)

        LOG.info('Releasing %s' % query)
        self.foreman.hosts_release(query)

    def reserve_hosts(self):
        query = self._build_query()
        LOG.info("Reserving %s" % query)
        try:
            hosts = self.foreman.hosts_reserve(query=query,
                                               reason=self.reserve_message,
                                               amount=self.count)
            LOG.info('Got hosts: %s' % hosts)
        except foreman_client.Unacceptable:
            LOG.info('No hosts available for reservation.')
            return None

        # unpack nested dict
        return [host['host'] for host in hosts]

    def reserve_hosts_or_wait(self):
        return common.wait_for(
            'wait for foreman reservation',
            lambda hosts: hosts and self.count == len(hosts),
            lambda: self.reserve_hosts(),
            self.wait_for_reservation,
            wait_sec=120)

    def show_reserved(self):
        query = self._build_query()
        reserved = self.foreman.show_reserved(query)
        if reserved:
            LOG.info('Still have reservation on: %s' % reserved)
        else:
            LOG.info('Nothing reserved with config: %s' % query)

    def _build_query(self):
        """Prepare query with conditions for foreman requests.

        Query is prepared based on arguments which were passed to this task.
        Included are existing_nodes (hostnames), hostgroup and hostname prefix.
        """
        conds = []
        if self.hostnames:
            conds.append('( %s )' % (
                ' or '.join(['name = %s' % hostname
                             for hostname in self.hostnames])))
        if self.hostgroup:
            conds.append("hostgroup ~ %s" % self.hostgroup)
        if self.prefix:
            conds.append("name ~ %s" % self.prefix)
        return ' and '.join(conds)

    def _reboot_host(self, host):
        LOG.info('Rebooting host: %s', host['name'])
        try:
            r = self.foreman.hosts.power(id=host['id'], power_action='reset')
        except foreman_client.ForemanException as e:
            LOG.error("Foreman failed to reboot a host")
            LOG.error(e)
        else:
            if r['power'] is True:
                LOG.info('Reboot host %s succeeded', host['name'])
                return

        # in case of failure try to reboot host in different/fallback way
        try:
            self._reboot_host_ipmi(host)
        except Exception as exc:
            LOG.warning(exc)
            self._reboot_host_ssh(host)

    def _reboot_host_ipmi(self, host):
        LOG.warning("Workaround foreman:"
                    " trying to do power reset directly with ipmitool")
        ipmi_ifcs = [ifc for ifc in host['interfaces']
                     if ifc.get('provider', '') == 'IPMI']
        ipmi_ifc = ipmi_ifcs[0]
        cmd = 'ipmitool -vI lanplus -U %s -P %s -H %s power reset'
        cmd = cmd % (ipmi_ifc['attrs']['username'],
                     ipmi_ifc['attrs']['password'],
                     ipmi_ifc['ip'])
        _local_cmd(cmd)

    def _reboot_host_ssh(self, host):
        LOG.warning('Workaround foreman: trying to reboot machine via ssh')
        old_ssh_wait = self.ssh_wait
        self.ssh_wait = 10  # for reprovisioning just wait short time or fail
        # this is already last safety net solution, will most likely fail too
        desc = self.connect_ips([host['ip']])
        for node in desc.nodes:
            node.cmd('reboot; exit 0')
        self.ssh_wait = old_ssh_wait

    def _puppet_unmanage(self, nodes):
        super(GetForemanNodesTask, self)._puppet_unmanage(nodes)

        def check_sortnics(node):
            """Verify that sort nics created valid files. """

            for eth_type in ('ETH_MANAGEMENT', 'ETH_VLAN'):
                ifc = node.cmd('[[ -f ~/%s ]] && cat ~/%s || echo ""'
                               % (eth_type, eth_type))
                if not ifc:
                    return False
            else:
                return True

        for node in [n for n in nodes if not check_sortnics(n)]:
            sort_nics_workaround(node)


def _local_cmd(cmd):
    """Execute command localy, raises exception when command failed.

    Returns tuple of (cmd, returncode, output):
    - cmd is the one passed as argument to this function
    - returncode is the exit code from the executed command
    - output contains both stdout and stderr (stderr=subprocess.STDOUT)

    If returncode is not zero, Exception is raised (it's msg contains the
    formatted tuple), otherwise the tuple is also logged with INFO level.
    """
    LOG.info('Executing %s:' % cmd)
    cmd_list = shlex.split(cmd)
    proc = subprocess.Popen(cmd_list,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    out = proc.communicate(None)[0]
    cmd_result = (cmd, proc.returncode, out)
    if proc.returncode != 0:
        raise Exception('Command "%s" returned %s:\n%s'
                        % cmd_result)
    LOG.info('%s returned %s\n%s' % cmd_result)
    return cmd_result


def sort_nics_workaround(node):
    """Baremetal host should have only 2 10G ifc.
     one with IP -> ETH_MANAGMENT
     one without -> ETH_VLAN
    """
    LOG.warning("workaround: puppet sortnics failed on node {node}."
                "applying workaround".format(node=node))

    # get facter into dict
    facter_dict = facter_to_dict(node)
    primary_ip = node.desc['ip']

    fqdn = facter_dict['fqdn']

    if fqdn.startswith("cougar") or fqdn.startswith("puma"):
        nic_speed = PUMA_SPEED
    else:
        nic_speed = IF_SPEED

    # get nics
    ifcs = facter_dict["interfaces"].split(',')
    for nic in ifcs:
        out = node.cmd("ethtool %s" % nic)
        speed = [line.strip() for line in out.splitlines()
                 if line.strip().startswith('Speed')]
        if speed:
            speed = speed[0].split()[1]
        out = node.cmd("ip a show %s" % nic)
        has_ip = len([n for n in out.splitlines() if primary_ip in n])
        file_suffix = None
        if has_ip:
            file_suffix = "MANAGEMENT"
        elif speed and speed.startswith("{sp}Mb".format(sp=nic_speed)):
            file_suffix = "VLAN"
            # run this command regardless of output
            node.cmd("ip link set %s up" % nic)

        if file_suffix:
            node.cmd("echo {nic} > /root/ETH_{suf}".
                     format(nic=nic, suf=file_suffix))


def facter_to_dict(node):
    """Foreman puppets save all data to a dict that can be retrieved using
    "facter"
     """
    out = node.cmd("facter")
    pre_dict = (line.strip().split("=>") for line in out.splitlines()
                if "=>" in line)

    # can't use dict comprehension in python2.6
    # return {k.strip(): v.strip() for k, v in pre_dict}
    return dict((k.strip(), v.strip()) for (k, v) in pre_dict)
