from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID82628_XEN_check_mapping_and_subscribe_fake_mode(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_XEN")

            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)
            xen_host_name = self.xen_get_hostname(xen_host_ip)
            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # (1) Check mapping info in fake mode
            # (1.1) Unregister xen hypervisor in server 
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_remove_system(xen_host_name, SERVER_IP)
            else:
                self.server_remove_system(host_uuid, SERVER_IP)
            # (1.2) Set xen fake mode, it will show host/guest mapping info
            fake_file = self.generate_fake_file("xen")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)

            # (2) Check bonus pool will created in fake mode
            # (2.1) Start guest and register guest to SAM
            self.xen_start_guest(guest_name, xen_host_ip)
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (2.2) Subscribe fake xen host
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_subscribe_system(xen_host_name, self.get_poolid_by_SKU(sku_id), SERVER_IP)
            else:
                self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), SERVER_IP)
            # (2.3) List available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, bonus_quantity, guestip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            self.sub_listconsumed(sku_name, guestip)

            # (3) Check bonus pool will revoke in fake mode
            # (3.1) Unsubscribe sku on xenisor
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_unsubscribe_all_system(xen_host_name, SERVER_IP)
            else:
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
            self.unset_all_virtwho_d_conf()
            self.set_xen_conf()
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_remove_system(xen_host_name, SERVER_IP)
            else:
                self.server_remove_system(host_uuid, SERVER_IP)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
