from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID82628_ESX_check_mapping_and_subscribe_fake_mode(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_ESX")

            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # (1) Check mapping info in fake mode
            # (1.1) Unregister esx hypervisor in server 
            self.server_remove_system(host_uuid, SERVER_IP)
            # (1.2) Set esx fake mode, it will show host/guest mapping info
            fake_file = self.generate_fake_file("esx")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)

            # (2) Check bonus pool will created in fake mode
            # (2.1) Start guest and register guest to SAM
            self.esx_start_guest(guest_name, esx_host_ip)
            guestip = self.esx_get_guest_ip(guest_name, esx_host_ip)
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (2.2) Subscribe fake esx host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), SERVER_IP)
            # (2.3) List available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, bonus_quantity, guestip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            self.sub_listconsumed(sku_name, guestip)

            # (3) Check bonus pool will revoke in fake mode
            # (3.1) Unsubscribe sku on hypervisor
            self.server_unsubscribe_all_system(host_uuid, SERVER_IP)
            # (3.2) Check consumed bonus pool revoke on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.server_remove_system(host_uuid, SERVER_IP)
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
