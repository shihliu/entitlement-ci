from utils import *
from utils.tools.shell import command
from utils.exception.failexception import FailException
from testcases.rhsm.rhsmconstants import RHSMConstants
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants

class Base(unittest.TestCase):
    # ========================================================
    #       Common Functions
    # ========================================================
    def cm_get_consumerid(self, targetmachine_ip=None):
        # get consumer id: system identity
        cmd = "subscription-manager identity | grep identity"
        (ret, output) = self.runcmd(cmd, "get consumerid", targetmachine_ip)
        return output.split(':')[1].strip()

    # ========================================================
    #       Basic Functions
    # ========================================================

    def runcmd(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        return command.runcmd(cmd, cmddesc, targetmachine_ip, targetmachine_user, targetmachine_pass, timeout, showlogger)

    def runcmd_esx(self, cmd, cmddesc=None, targetmachine_ip=None, timeout=None, showlogger=True):
        return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "qwer1234P!", timeout, showlogger)

    def runcmd_sam(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        return self.runcmd(cmd, cmddesc, targetmachine_ip, "root", "redhat", timeout, showlogger)

    def runcmd_interact(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
        return command.runcmd_interact(cmd, cmddesc, targetmachine_ip, targetmachine_user, targetmachine_pass, timeout, showlogger)

    def get_os_serials(self, targetmachine_ip=None):
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
        (ret, output) = self.runcmd(cmd, "get system version", targetmachine_ip=targetmachine_ip, showlogger=False)
        if ret == 0:
            return output.strip("\n").strip(" ")
        else: raise FailException("Failed to get os serials")

    def get_server_info(self):
        # usage: server_ip, server_hostname, server_user, server_pass = self.get_server_info()
        return get_exported_param("SERVER_IP"), get_exported_param("SERVER_HOSTNAME"), self.get_vw_cons("username"), self.get_vw_cons("password")

    def get_hg_info(self, targetmachine_ip=None):
        if targetmachine_ip == "" or targetmachine_ip == None:
            host_guest_info = "in host machine"
        else:
            host_guest_info = "in guest machine %s" % targetmachine_ip
        return host_guest_info

    def get_rhsm_cons(self, name):
        rhsm_cons = RHSMConstants()
        if self.test_server == "SAM":
            if self.os_serial == "7" and name + "_el7" in rhsm_cons.sam_cons:
                return rhsm_cons.sam_cons[name + "_el7"]
            else:
                return rhsm_cons.sam_cons[name]
        elif self.test_server == "SATELLITE":
            if self.os_serial == "7" and name + "_el7" in rhsm_cons.sam_cons:
                return rhsm_cons.sam_cons[name + "_el7"]
            elif name + "_sat" in rhsm_cons.sam_cons:
                return rhsm_cons.sam_cons[name + "_sat"]
            else:
                return rhsm_cons.sam_cons[name]
        elif self.test_server == "STAGE" :
            if self.os_serial == "7" and name + "_el7" in rhsm_cons.stage_cons:
                return rhsm_cons.stage_cons[name + "_el7"]
            else:
                return rhsm_cons.stage_cons[name]
        else:
            raise FailException("Failed to get rhsm constant %s" % name)

    def get_vw_cons(self, name):
        virtwho_cons = VIRTWHOConstants()
        if self.test_server == "SAM":
            return virtwho_cons.virtwho_sam_cons[name]
        elif self.test_server == "SATELLITE":
            return virtwho_cons.virtwho_satellite_cons[name]
        elif self.test_server == "STAGE" :
            return virtwho_cons.virtwho_stage_cons[name]
        else:
            raise FailException("Failed to get virt-who constant %s" % name)

    def get_vw_guest_name(self, guest_name):
        return VIRTWHOConstants().virtwho_cons[guest_name] + "_" + self.test_server.capitalize()

    def get_locator(self, name):
        rhsm_gui_locator = RHSMGuiLocator()
        if name + "-" + self.os_serial in rhsm_gui_locator.element_locators.keys():
            return rhsm_gui_locator.element_locators[name + "-" + self.os_serial]
        else:
            return rhsm_gui_locator.element_locators[name]

    def service_command(self, command, targetmachine_ip="", is_return=False):
        virtwho_cons = VIRTWHOConstants()
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = virtwho_cons.virt_who_commands[command + "_systemd"]
        else:
            cmd = virtwho_cons.virt_who_commands[command]
        ret, output = self.runcmd(cmd, "run cmd: %s" % cmd, targetmachine_ip)
        if is_return == True:
            if ret == 0:
                logger.info("Succeeded to run cmd %s in %s." % (cmd, self.get_hg_info(targetmachine_ip)))
                return True
            else:
                return False
        else:
            if ret == 0:
                logger.info("Succeeded to run cmd %s in %s." % (cmd, self.get_hg_info(targetmachine_ip)))
                return output
            else:
                raise FailException("Test Failed - Failed to run cmd in %s." % (cmd, self.get_hg_info(targetmachine_ip)))

    # ========================================================
    #       Configure Server Functions
    # ========================================================

    def configure_sam_host(self, samhostip, samhostname, targetmachine_ip=""):
        self.configure_host_file(samhostip, samhostname, targetmachine_ip)
        cmd = "rpm -qa | grep candlepin-cert-consumer | xargs rpm -e"
        ret, output = self.runcmd(cmd, "if candlepin-cert-consumer package exist, remove it.", targetmachine_ip)
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)
        cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
        ret, output = self.runcmd(cmd, "install candlepin cert", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
        else:
            raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)

    def configure_satellite_host(self, satellitehostip, satellitehostname, targetmachine_ip=""):
        if "satellite" in satellitehostname:
            # for satellite installed in qeos
            satellitehostname = satellitehostname + ".novalocal"
        self.configure_host_file(satellitehostip, satellitehostname, targetmachine_ip)
        cmd = "rpm -qa | grep katello-ca-consumer | xargs rpm -e"
        ret, output = self.runcmd(cmd, "if katello-ca-consumer package exist, remove it.", targetmachine_ip)
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)
        cmd = "rpm -ivh http://%s/pub/katello-ca-consumer-latest.noarch.rpm" % (satellitehostip)
        ret, output = self.runcmd(cmd, "install katello-ca-consumer-latest.noarch.rpm", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with satellite configuration.")
        else:
            raise FailException("Failed to install candlepin cert and configure the system with satellite configuration.")

    def configure_host_file(self, server_ip, server_hostname, targetmachine_ip=""):
        cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (server_ip, server_ip, server_hostname)
        ret, output = self.runcmd(cmd, "configure /etc/hosts", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure /etc/hosts")
        else:
            raise FailException("Failed to configure /etc/hosts")

    def configure_stage_host(self, stage_name, targetmachine_ip=""):
        cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % stage_name
        ret, output = self.runcmd(cmd, "configure rhsm.conf for stage", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure rhsm.conf for stage")
        else:
            raise FailException("Failed to configure rhsm.conf for stage")
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)

    def configure_baseurl(self, baseurl, targetmachine_ip=""):
        cmd = "sed -i -e 's/cdn.redhat.com/%s/g' /etc/rhsm/rhsm.conf" % baseurl
        ret, output = self.runcmd(cmd, "configure baseurl for stage", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure baseurl for stage")
        else:
            raise FailException("Failed to configure baseurl for stage")
        cmd = "subscription-manager clean"
        ret, output = self.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)

    def configure_server(self, server_ip="", server_hostname="", targetmachine_ip=""):
        if self.test_server == "STAGE" :
            self.configure_stage_host("subscription.rhn.stage.redhat.com", targetmachine_ip)
            self.configure_baseurl("subscription.rhn.stage.redhat.com", targetmachine_ip)
        else:
            if server_ip == "" or server_hostname == "":
                server_ip = get_exported_param("SERVER_IP")
                server_hostname = get_exported_param("SERVER_HOSTNAME")
            if self.test_server == "SAM" :
                self.configure_sam_host(server_ip, server_hostname, targetmachine_ip)
            elif self.test_server == "SATELLITE" :
                self.configure_satellite_host(server_ip, server_hostname, targetmachine_ip)
            else:
                raise FailException("Test Failed - Failed to configure rhsm testing server ... ")

    # ========================================================
    #       SAM Functions
    # ========================================================

    def server_check_system(self, system_uuid, destination_ip=None):
        ''' check system exist in test server '''
        if self.test_server == "SATELLITE":
            uuid = self.st_name_to_id(system_uuid)
            output = self.st_system_list()
            if uuid in output:
                logger.info("Succeeded to check system %s exist in test server" % uuid)
            else:
                raise FailException("Failed to check system %s exist in test server" % uuid)
        else:
            cmd = "headpin -u admin -p admin system list --org=ACME_Corporation --environment=Library"
            ret, output = self.runcmd_sam(cmd, "check system exist in sam server", destination_ip)
            if ret == 0 and system_uuid in output:
                logger.info("Succeeded to check system %s exist in test server" % system_uuid)
            else:
                raise FailException("Failed to check system %s exist in test server" % system_uuid)

    def server_remove_system(self, system_uuid, destination_ip=None):
        ''' remove system in test server '''
        if self.test_server == "SATELLITE":
            uuid = self.st_name_to_id(system_uuid)
            output = self.st_system_remove(uuid)
            logger.info("Succeeded to remove system %s in test server" % uuid)
        elif self.test_server == "STAGE":
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            baseurl = "https://subscription.rhn.stage.redhat.com:443" + "/subscription"
            cmd = "curl -X DELETE -k -u %s:%s %s/consumers/%s" % (username, password, baseurl, system_uuid)
            (ret, output) = self.runcmd(cmd, "delete consumer from test server")
            if ret == 0:
                logger.info("It's successful to delete consumer from test server.")
            else:
                raise FailException("Test Failed - Failed to delete consumer from test server.")
        else:
            cmd = "headpin -u admin -p admin system unregister --name=%s --org=ACME_Corporation" % system_uuid
            ret, output = self.runcmd_sam(cmd, "remove system in sam server", destination_ip)
            if ret == 0 and system_uuid in output:
                logger.info("Succeeded to remove system %s in test server" % system_uuid)
            else:
                raise FailException("Failed to remove system %s in test server" % system_uuid)

    def server_subscribe_system(self, system_uuid, poolid, destination_ip=None):
        ''' subscribe host in test server '''
        if self.test_server == "SATELLITE":
            uuid = self.st_name_to_id(system_uuid)
            self.st_attach(uuid, poolid)
            logger.info("Succeeded to subscribe host %s in test server" % uuid)
        else:
            cmd = "headpin -u admin -p admin system subscribe --name=%s --org=ACME_Corporation --pool=%s " % (system_uuid, poolid)
            ret, output = self.runcmd_sam(cmd, "subscribe host in sam server", destination_ip)
            if ret == 0 and system_uuid in output:
                logger.info("Succeeded to subscribe host %s in sam server" % system_uuid)
            else:
                raise FailException("Failed to subscribe host %s in sam server" % system_uuid)

    def server_unsubscribe_all_system(self, system_uuid, destination_ip=None):
        ''' unsubscribe host in test server '''
        if self.test_server == "SATELLITE":
            uuid = self.st_name_to_id(system_uuid)
            self.st_unattach_all(uuid)
            logger.info("Succeeded to unsubscribe host %s in test server" % uuid)
        else:
            cmd = "headpin -u admin -p admin system unsubscribe --name=%s --org=ACME_Corporation --all" % system_uuid
            ret, output = self.runcmd_sam(cmd, "unsubscribe host in sam server", destination_ip)
            if ret == 0 and system_uuid in output:
                logger.info("Succeeded to unsubscribe host %s in sam server" % system_uuid)
            else:
                raise FailException("Failed to unsubscribe host %s in sam server" % system_uuid)

    # ========================================================
    #       SATELLITE Functions
    # ========================================================

    def st_orgs_list(self):
        return self.get_json("organizations/")

    def st_org_create(self, org_name):
        location = "organizations/"
        json_data = json.dumps({"name": org_name})
        return self.post_json(location, json_data)["id"]

    def st_org_update(self, org_id):
        location = "organizations/%s" % org_id
        json_data = json.dumps({"name": "change name"})
        self.put_json(location, json_data)

    def st_org_delete(self, org_id):
        self.delete_json("organizations/%s" % org_id)

    def st_users_list(self):
        return self.get_json("users/")

    # do not know how to setup auth_source_id, failed func
    def st_user_create(self, user_name, user_pass):
        location = "users/"
        json_data = json.dumps({"login":user_name, "password":user_pass, "admin":"true", "mail":"test@redhat.com", "auth_source_id": 1})
        return self.post_json(location, json_data)["id"]

    def st_attach(self, uuid, pool_id):
        location = "systems/%s/subscriptions/" % uuid
        json_data = json.dumps({"uuid":uuid, "subscriptions":[{"id":pool_id, "quantity":0}]})
        return self.post_json(location, json_data)["results"][1]["id"]

    def st_unattach(self, uuid, consumed_pool_id):
        location = "systems/%s/subscriptions/%s" % (uuid, consumed_pool_id)
        return self.delete_json(location)

    def st_unattach_all(self, uuid):
        for consumed_pool_id in self.st_consumed_list(uuid):
            self.st_unattach(uuid, consumed_pool_id)

    def st_system_list(self):
        return self.get_json("systems/")

    def st_system_remove(self, uuid):
        return self.delete_json("systems/%s" % uuid)

    def st_consumed_list(self, uuid):
        consumed_id_list = []
        all_consumed = self.get_json("systems/%s/subscriptions" % uuid)["results"]
        for consumed in all_consumed:
            consumed_id_list.append(consumed["id"])
        return consumed_id_list

    def st_name_to_id(self, name):
        systems = self.st_system_list()["results"]
        for item in systems:
            if item["name"] == name:
                return item["id"]
        raise FailException("Failed to get id by system name: %s" % name)

    def get_json(self, location):
        """
        Performs a GET using the passed URL location
        """
        server_ip, server_hostname, username, password = self.get_server_info()
        sat_api = "https://%s/katello/api/v2/%s" % (server_ip, location)
        result = requests.get(
            sat_api,
            auth=(username, password),
            verify=False)
        ret, output = result.status_code, result.json()
        logger.info("Status Code >>>: %s" % ret)
        logger.info("Result >>>: %s" % output)
        if ret not in (200,):
            raise FailException("Failed to run requests get: %s" % sat_api)
        else:
            logger.info("Succeeded to run requests get: %s" % sat_api)
            return output

    def post_json(self, location, json_data):
        """
        Performs a POST and passes the data to the URL location
        """
        server_ip, server_hostname, username, password = self.get_server_info()
        sat_api = "https://%s/katello/api/v2/%s" % (server_ip, location)
        post_headers = {'content-type': 'application/json'}
        result = requests.post(
            sat_api,
            data=json_data,
            auth=(username, password),
            verify=False,
            headers=post_headers)
        ret, output = result.status_code, result.json()
        logger.info("Status Code >>>: %s" % ret)
        logger.info("Result >>>: %s" % output)
        if ret not in (200, 201):
            raise FailException("Failed to run requests post: %s" % sat_api)
        else:
            logger.info("Succeeded to run requests post: %s" % sat_api)
            return output

    def put_json(self, location, json_data):
        """
        Performs a PUT and passes the data to the URL location
        """
        server_ip, server_hostname, username, password = self.get_server_info()
        sat_api = "https://%s/katello/api/v2/%s" % (server_ip, location)
        post_headers = {'content-type': 'application/json'}
        result = requests.put(
            sat_api,
            data=json_data,
            auth=(username, password),
            verify=False,
            headers=post_headers)
        ret, output = result.status_code, result.json()
        logger.info("Status Code >>>: %s" % ret)
        logger.info("Result >>>: %s" % output)
        if ret not in (200,):
            raise FailException("Failed to run requests put: %s" % sat_api)
        else:
            logger.info("Succeeded to run requests put: %s" % sat_api)
            return output

    def delete_json(self, location):
        """
        Performs a DELETE using the passed URL location
        """
        server_ip, server_hostname, username, password = self.get_server_info()
        sat_api = "https://%s/katello/api/v2/%s" % (server_ip, location)
        result = requests.delete(
            sat_api,
            auth=(username, password),
            verify=False)
        ret, output = result.status_code, result
        logger.info("Status Code >>>: %s" % ret)
        logger.info("Result >>>: %s" % output)
        if ret not in (200, 202, 204):
            raise FailException("Failed to run requests delete: %s" % sat_api)
        else:
            logger.info("Succeeded to run requests delete: %s" % sat_api)
            return output

    # ========================================================
    #       Skip Test Functions
    # ========================================================

    def skip_on_rhel7(self):
        if self.os_serial == "7" :
            logger.info("rhel 7.x do not support, this test case is skipped ...")
            return True
        else: return False

    def skip_satellite(self):
        if self.test_server == "SATELLITE" :
            logger.info("satellite do not support, this test case is skipped ...")
            return True
        else: return False

    # ========================================================
    #       unittest setup
    # ========================================================
    def setUp(self):
        # show log in unittest report
        self.unittest_handler = logging.StreamHandler(sys.stdout)
        self.unittest_handler.setFormatter(formatter)
        logger.addHandler(self.unittest_handler)
        # logger.removeHandler(ch)

        logger.info(" ")
        logger.info("**************************************************************************************************************")
        self.os_serial = self.get_os_serials()
        self.test_server = get_exported_param("SERVER_TYPE")
        logger.info("********** Begin Running ...**** OS: RHEL %s **** Server: %s **********" % (self.os_serial, self.test_server))
        SERVER_IP = get_exported_param("SERVER_IP")
        SERVER_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
        REMOTE_IP = get_exported_param("REMOTE_IP")
        REMOTE_IP_2 = get_exported_param("REMOTE_IP_2")
        RHEL_COMPOSE = get_exported_param("RHEL_COMPOSE")
        BREW_VIRTWHO = get_exported_param("BREW_VIRTWHO")
        logger.info("**************************************************************************************************************")

    def tearDown(self):
        logger.removeHandler(self.unittest_handler)
        # logger.addHandler(ch)

#     def test_self(self):
#         org = self.st_org_create("autoorg20")
#         self.st_orgs_list()
#         self.st_org_update(org)
#         self.st_orgs_list()
#         self.st_org_delete(org)
#         self.st_orgs_list()
#         consumed_pool_id = self.st_attach("43e33262-57ff-4b13-ba94-1e5459cba2a2", "2c90ec93507e9bf901507ea2b2e601a7")
#         self.st_unattach("43e33262-57ff-4b13-ba94-1e5459cba2a2", consumed_pool_id)
#         id = self.st_name_to_id("aee4ff00-8c33-11e2-994a-6c3be51d959a")
#         logger.info(id)

if __name__ == "__main__":
    unittest.main()
