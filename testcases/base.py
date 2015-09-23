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
    #       SAM Functions
    # ========================================================
    def esx_check_host_in_samserv(self, esx_uuid, destination_ip):
        ''' check esx host exist in sam server '''
        cmd = "headpin -u admin -p admin system list --org=ACME_Corporation --environment=Library"
        ret, output = self.runcmd_sam(cmd, "check esx host exist in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
        # if ret == 0 and output.find(esx_uuid) >= 0:
            logger.info("Succeeded to check esx host %s exist in sam server" % esx_uuid)
        else:
            raise FailException("Failed to check esx host %s exist in sam server" % esx_uuid)

    def esx_remove_host_in_samserv(self, esx_uuid, destination_ip):
        ''' remove esx host in sam server '''
        cmd = "headpin -u admin -p admin system unregister --name=%s --org=ACME_Corporation" % esx_uuid
        ret, output = self.runcmd_sam(cmd, "remove esx host in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to remove esx host %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to remove esx host %s in sam server" % esx_uuid)

    def esx_remove_deletion_record_in_samserv(self, esx_uuid, destination_ip):
        ''' remove deletion record in sam server '''
        cmd = "headpin -u admin -p admin system remove_deletion --uuid=%s" % esx_uuid
        ret, output = self.runcmd_sam(cmd, "remove deletion record in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to remove deletion record %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to remove deletion record %s in sam server" % esx_uuid)

    def esx_subscribe_host_in_samserv(self, esx_uuid, poolid, destination_ip):
        ''' subscribe host in sam server '''
        cmd = "headpin -u admin -p admin system subscribe --name=%s --org=ACME_Corporation --pool=%s " % (esx_uuid, poolid)
        ret, output = self.runcmd_sam(cmd, "subscribe host in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to subscribe host %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to subscribe host %s in sam server" % esx_uuid)

    def esx_unsubscribe_all_host_in_samserv(self, esx_uuid, destination_ip):
        ''' unsubscribe host in sam server '''
        cmd = "headpin -u admin -p admin system unsubscribe --name=%s --org=ACME_Corporation --all" % esx_uuid
        ret, output = self.runcmd_sam(cmd, "unsubscribe host in sam server", destination_ip)
        if ret == 0 and esx_uuid in output:
            logger.info("Succeeded to unsubscribe host %s in sam server" % esx_uuid)
        else:
            raise FailException("Failed to unsubscribe host %s in sam server" % esx_uuid)
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
