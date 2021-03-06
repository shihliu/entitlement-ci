from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID82635_XEN_validate_limited_bonus_creat_and_remove(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            test_sku = self.get_vw_cons("productid_guest")
            bonus_quantity = self.get_vw_cons("guestlimit")
            sku_name = self.get_vw_cons("productname_guest")

            self.xen_start_guest(guest_name, xen_host_ip)
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)
            hostuuid = self.xen_get_host_uuid(xen_host_ip)
            xen_host_name = self.xen_get_hostname(xen_host_ip)
            self.runcmd_service("restart_virtwho")

            # (1) Check limited bonus pool will create after subscribe pool on hypervisor
            # (1.1) Start guest
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            self.sub_disable_auto_subscribe(guestip)
            # (1.2) Hypervisor subscribe physical pool which can generate limited bonus pool
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_subscribe_system(xen_host_name, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            else:
                self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # (1.3) list available pools on guest, check limited bonus pool generated.
            self.check_bonus_exist(test_sku, bonus_quantity, guestip)
            # (1.4)subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)

            # (2) Check limited bonus pool will revoke after unsubscribe pool on hypervisor
            # (2.1) Unsubscribe sku on hypervisor
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_unsubscribe_all_system(xen_host_name, SERVER_IP)
            else:
                self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
            # (2.2) Check consumed bonus pool revoke on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # unsubscribe all subscriptions on  hypervisor
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
#             self.xen_stop_guest(guest_name, xen_host_ip)
            if "ohsnap-satellite63" in get_exported_param("SERVER_COMPOSE"):
                self.server_unsubscribe_all_system(xen_host_name, SERVER_IP)
            else:
                self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
