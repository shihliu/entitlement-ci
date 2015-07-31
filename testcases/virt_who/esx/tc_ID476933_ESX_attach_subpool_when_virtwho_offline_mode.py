from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID476933_ESX_attach_subpool_when_virtwho_offline_mode(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            VIRTWHO_ESX_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_OWNER")
            VIRTWHO_ESX_ENV = VIRTWHOConstants().get_constant("VIRTWHO_ESX_ENV")
            VIRTWHO_ESX_SERVER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
            VIRTWHO_ESX_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
            VIRTWHO_ESX_PASSWORD = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")

            product_name = VIRTWHOConstants().get_constant("datacenter_name")
            host_sku_id = VIRTWHOConstants().get_constant("datacenter_sku_id")
            bonus_sku_id = VIRTWHOConstants().get_constant("datacenter_bonus_sku_id")
            bonus_quantity = VIRTWHOConstants().get_constant("datacenter_bonus_quantity")

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the guest is power off or not on esxi host, if power on, stop it firstly 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1). stop virt-who firstly 
            self.service_command("stop_virtwho")

            #2). disable esx config
            self.unset_esx_conf()

            #3). create offline data
            offline_data = "/tmp/offline.dat"
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -p -d > %s" %(VIRTWHO_ESX_OWNER,VIRTWHO_ESX_ENV,VIRTWHO_ESX_SERVER,VIRTWHO_ESX_USERNAME,VIRTWHO_ESX_PASSWORD,offline_data)
            ret, output = self.runcmd(cmd, "executing virt-who with -p -d for offline mode.")
            if ret == 0:
                logger.info("Succeeded to execute virt-who with -p -d for offline mode. ")
            else:
                raise FailException("Failed to execute virt-who with -o -d")

            #4). creat /etc/virt-who.d/virt.fake file for offline mode
            conf_file = "/etc/virt-who.d/virt.fake"
            conf_data = '''[fake-virt]
type=fake
file=%s
is_hypervisor=True
owner=%s
env=%s''' % (offline_data, VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV)

            self.set_virtwho_d_conf(conf_file, conf_data)

            #5). virt-who restart
            self.service_command("restart_virtwho")

            #6). check whether the host/guest association info has been sent to server
            if self.esx_check_uuid_exist_in_rhsm_log(host_uuid) and self.esx_check_uuid_exist_in_rhsm_log(guestuuid):
                logger.info("Succeeded to get uuid list from rhsm.log.")
            else:
                raise FailException("Failed to get uuid list from rhsm.log")

            #7).check DataCenter is exist on host/hpyervisor
            host_pool_id = self.get_poolid_by_SKU(host_sku_id)
            if host_pool_id is not None or host_pool_id !="":
                 logger.info("Succeeded to find the pool id of '%s': '%s'" % (host_sku_id, host_pool_id))
            else:
                raise FailException("Failed to find the pool id of %s" % host_sku_id)

            #8).register guest to SAM/Candlepin server with same username and password
            if not self.sub_isregistered(guestip):
                self.configure_host(SAM_HOSTNAME, SAM_IP, guestip)
                self.sub_register(SAM_USER, SAM_PASS, guestip)

            #9).subscribe successfully to the DataCenter subscription pool on host
            self.esx_subscribe_host_in_samserv(host_uuid, host_pool_id, SAM_IP)

            #10).check the bonus pool is available
            if self.check_bonus_isExist(bonus_sku_id, bonus_quantity, guestip) is True:
                logger.info("Succeeded to find the bonus pool of product '%s'" % product_name)
                self.assert_(True, case_name)
            else:
                raise FailException("Failed to find the bonus pool from guest.")

            #11).subscribe to the bonus pool. 
            self.sub_subscribe_sku(bonus_sku_id, guestip)

            #12).check the Status Details of consumed product
            consumed_status_key = "StatusDetails"
            consumed_status_value = "Subscription is current"
            if self.check_consumed_status(bonus_sku_id, consumed_status_key, consumed_status_value, guestip):
                logger.info("Succeeded to check the consumed Status Details: Subscription is current")
            else:
                raise FailException("Failed to check the consumed Status Details.")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file)

            cmd = "rm -f %s" % offline_data
            self.runcmd(cmd, "run cmd: %s" % cmd)

            self.set_esx_conf()
            self.service_command("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

