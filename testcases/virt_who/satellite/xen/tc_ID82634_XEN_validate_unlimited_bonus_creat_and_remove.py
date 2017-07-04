from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID82634_XEN_validate_unlimited_bonus_creat_and_remove(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            host_uuid = self.xen_get_host_uuid(xen_host_ip)
            xen_host_name = self.xen_get_hostname(xen_host_ip)

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")
            sku_quantity = self.get_vw_cons("guestlimit_unlimited_guest")

            # (1) Check unlimited bonus pool will create after subscribe pool on hypervisor
            # (1.1) Start guest
            self.xen_start_guest(guest_name, xen_host_ip)
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)
            self.runcmd_service("restart_virtwho")
            # (1.2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            # (1.3) Subscribe hypervisor
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_subscribe_system(xen_host_name, self.get_poolid_by_SKU(sku_id), server_ip)
            else:
                self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), server_ip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            # (1.4) List available pools of guest, check related bonus pool generated.
            self.sub_listconsumed(sku_name, guestip)

            # (2) Check unlimited bonus pool will revoke after unsubscribe pool on hypervisor
            # (2.1) Unsubscribe sku on hypervisor
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_unsubscribe_all_system(xen_host_name, server_ip)
            else:
                self.server_unsubscribe_all_system(host_uuid, server_ip)
            # (2.2) Check consumed bonus pool revoke on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
#             self.xen_stop_guest(guest_name, xen_host_ip)
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_unsubscribe_all_system(xen_host_name, server_ip)
            else:
                self.server_unsubscribe_all_system(host_uuid, server_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
