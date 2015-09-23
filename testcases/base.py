from utils import *
from utils.tools.shell import command
from utils.exception.failexception import FailException
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants

class Base(unittest.TestCase):
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
        else:
            raise FailException("Failed to get os serials")

    # ========================================================
    #       Configure Server Functions
    # ========================================================

    def configure_sam_host(self, samhostip, samhostname, targetmachine_ip=""):
        cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
        ret, output = command.runcmd(cmd, "configure /etc/hosts", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure /etc/hosts")
        else:
            raise FailException("Failed to configure /etc/hosts")
        cmd = "rpm -qa | grep candlepin-cert-consumer"
        ret, output = command.runcmd(cmd, "check candlepin cert", targetmachine_ip)
        if ret == 0:
            logger.info("candlepin-cert-consumer-%s-1.0-1.noarch has already exist, remove it first." % samhostname)
            cmd = "rpm -e candlepin-cert-consumer-%s-1.0-1.noarch" % samhostname
            ret, output = command.runcmd(cmd, "uninstall candlepin cert", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
            else:
                raise FailException("Failed to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
        cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
        ret, output = command.runcmd(cmd, "install candlepin cert", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
        else:
            raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)

    def configure_satellite_host(self, satellitehostip, satellitehostname, targetmachine_ip=""):
        if "satellite" in satellitehostname:
            # for satellite installed in qeos
            satellitehostname = satellitehostname + ".novalocal"
        cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (satellitehostname, satellitehostip, satellitehostname)
        ret, output = command.runcmd(cmd, "configure /etc/hosts", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure /etc/hosts")
        else:
            raise FailException("Failed to configure /etc/hosts")
        cmd = "rpm -qa | grep katello-ca-consumer | xargs rpm -e"
        ret, output = command.runcmd(cmd, "if katello-ca-consumer package exist, remove it.", targetmachine_ip)
        cmd = "subscription-manager clean"
        ret, output = command.runcmd(cmd, "run subscription-manager clean", targetmachine_ip)
        cmd = "rpm -ivh http://%s/pub/katello-ca-consumer-latest.noarch.rpm" % (satellitehostip)
        ret, output = command.runcmd(cmd, "install katello-ca-consumer-latest.noarch.rpm", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to install candlepin cert and configure the system with satellite configuration.")
        else:
            raise FailException("Failed to install candlepin cert and configure the system with satellite configuration.")

    def configure_stage_host(self, stage_name, targetmachine_ip=""):
        cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % stage_name
        ret, output = command.runcmd(cmd, "configure rhsm.conf for stage", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to configure rhsm.conf for stage")
        else:
            raise FailException("Failed to configure rhsm.conf for stage")

    def configure_testing_server(self, server_ip="", server_hostname="", targetmachine_ip=""):
        test_server = get_exported_param("SERVER_TYPE")
        if test_server == "STAGE" :
            self.configure_stage_host("subscription.rhn.stage.redhat.com", targetmachine_ip)
        else:
            if server_ip == "" or server_hostname == "":
                server_ip = get_exported_param("SERVER_IP")
                server_hostname = get_exported_param("SERVER_HOSTNAME")
            if test_server == "SAM" :
                self.configure_sam_host(server_ip, server_hostname, targetmachine_ip)
            elif test_server == "SATELLITE" :
                self.configure_satellite_host(server_ip, server_hostname, targetmachine_ip)
            else:
                raise FailException("Test Failed - Failed to configure rhsm testing server ... ")

    # ========================================================
    #       SAM Functions
    # ========================================================

    def check_system_in_samserv(self, system_uuid, destination_ip):
        ''' check system exist in sam server '''
        cmd = "headpin -u admin -p admin system list --org=ACME_Corporation --environment=Library"
        ret, output = self.runcmd_sam(cmd, "check system exist in sam server", destination_ip)
        if ret == 0 and system_uuid in output:
            logger.info("Succeeded to check system %s exist in sam server" % system_uuid)
        else:
            raise FailException("Failed to check system %s exist in sam server" % system_uuid)

    def remove_system_in_samserv(self, system_uuid, destination_ip):
        ''' remove system in sam server '''
        cmd = "headpin -u admin -p admin system unregister --name=%s --org=ACME_Corporation" % system_uuid
        ret, output = self.runcmd_sam(cmd, "remove system in sam server", destination_ip)
        if ret == 0 and system_uuid in output:
            logger.info("Succeeded to remove system %s in sam server" % system_uuid)
        else:
            raise FailException("Failed to remove system %s in sam server" % system_uuid)

    def remove_deletion_record_in_samserv(self, system_uuid, destination_ip):
        ''' remove deletion record in sam server '''
        cmd = "headpin -u admin -p admin system remove_deletion --uuid=%s" % system_uuid
        ret, output = self.runcmd_sam(cmd, "remove deletion record in sam server", destination_ip)
        if ret == 0 and system_uuid in output:
            logger.info("Succeeded to remove deletion record %s in sam server" % system_uuid)
        else:
            raise FailException("Failed to remove deletion record %s in sam server" % system_uuid)

    def subscribe_system_in_samserv(self, system_uuid, poolid, destination_ip):
        ''' subscribe host in sam server '''
        cmd = "headpin -u admin -p admin system subscribe --name=%s --org=ACME_Corporation --pool=%s " % (system_uuid, poolid)
        ret, output = self.runcmd_sam(cmd, "subscribe host in sam server", destination_ip)
        if ret == 0 and system_uuid in output:
            logger.info("Succeeded to subscribe host %s in sam server" % system_uuid)
        else:
            raise FailException("Failed to subscribe host %s in sam server" % system_uuid)

    def unsubscribe_all_system_in_samserv(self, system_uuid, destination_ip):
        ''' unsubscribe host in sam server '''
        cmd = "headpin -u admin -p admin system unsubscribe --name=%s --org=ACME_Corporation --all" % system_uuid
        ret, output = self.runcmd_sam(cmd, "unsubscribe host in sam server", destination_ip)
        if ret == 0 and system_uuid in output:
            logger.info("Succeeded to unsubscribe host %s in sam server" % system_uuid)
        else:
            raise FailException("Failed to unsubscribe host %s in sam server" % system_uuid)

    # ========================================================
    #       SATELLITE Functions
    # ========================================================

    # List system
    def st_system_list(self):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems" % server_ip
        res = requests.get(api_url, auth=(username, password), verify=False)
        return res.json()

    # List pool list
    def st_pool_list(self, uuid):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems/%s/subscriptions/available" % (server_ip, uuid)
        res = requests.get(api_url, auth=(username, password), verify=False)
        return res.json()

    # Attach pool_id 
    def st_attach(self, uuid, pool_id):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems/%s/subscriptions" % (server_ip, uuid)
        post_headers = {'content-type': 'application/json'}
        json_data = json.dumps({"uuid":uuid, "subscriptions":[{"id":pool_id, "quantity":0}]})
        res = requests.post(
              api_url,
              data=json_data,
              auth=(username, password),
              verify=False,
              headers=post_headers)
        return res.json()

    # List consumed 
    def st_consumed_list(self, uuid):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems/%s/subscriptions" % (server_ip, uuid)
        res = requests.get(api_url, auth=(username, password), verify=False)
        return res.json()

    # Unattach poo_id
    def st_unattach(self, uuid, pool_id):
        server_ip = get_exported_param("SERVER_IP")
        username = VIRTWHOConstants().get_constant("SAM_USER")
        password = VIRTWHOConstants().get_constant("SAM_PASS")
        api_url = "https://%s/katello/api/v2/systems/%s/subscriptions" % (server_ip, uuid)
        post_headers = {'content-type': 'application/json'}
        json_data = json.dumps({"uuid":uuid, "subscriptions":[{"subscription_id":pool_id}]})
        res = requests.put(
              api_url,
              data=json_data,
              auth=(username, password),
              verify=False,
              headers=post_headers,)
        return res.json()

    # ========================================================
    #       Skip Test Functions
    # ========================================================

    def skip_on_rhel7(self):
        rhel_version = self.get_os_serials()
        if rhel_version == "7" :
            logger.info("rhel 7.x do not support, this test case is skipped ...")
            return True
        else:
            return False

    def against_satellite(self):
        test_server = get_exported_param("SERVER_TYPE")
        if test_server == "SATELLITE" :
            logger.info("satellite do not support, this test case is skipped ...")
            return True
        else:
            return False
