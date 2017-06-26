from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17250_HYPERV_check_bonus_subscribe_in_fake_mode(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_HYPERV")
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            hyperv_host_ip = self.get_vw_cons("HYPERV_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()
            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # (1) Unregister hyperv hypervisor in server 
            self.server_remove_system(host_uuid, SERVER_IP)
            # (2) Register hyperv hypervisor with fake mode
            fake_file = self.generate_fake_file("hyperv")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Start guest and register guest to SAM
            self.hyperv_start_guest(guest_name)
            guestip = self.hyperv_get_guest_ip(guest_name)
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (4) Subscribe fake hyperv host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), SERVER_IP)
            # (5) List available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, bonus_quantity, guestip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            self.sub_listconsumed(sku_name, guestip)
            # (6) Unregister fake hyperv hypervisor in server 
            self.runcmd_service("stop_virtwho")
            self.server_remove_system(host_uuid, SERVER_IP)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.sub_unregister(guestip)
            self.hyperv_stop_guest(guest_name)
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
