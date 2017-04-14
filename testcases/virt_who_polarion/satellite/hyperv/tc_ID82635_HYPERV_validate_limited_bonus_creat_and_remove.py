from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID82635_HYPERV_validate_limited_bonus_creat_and_remove(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            test_sku = self.get_vw_cons("productid_guest")
            bonus_quantity = self.get_vw_cons("guestlimit")
            sku_name = self.get_vw_cons("productname_guest")

            self.runcmd_service("restart_virtwho")

            self.hyperv_start_guest(guest_name)
            guestip = self.hyperv_get_guest_ip(guest_name)
            hostuuid = self.hyperv_get_host_uuid()

            # (1) Check limited bonus pool will create after subscribe pool on hypervisor
            # (1.1) Start guest
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            self.sub_disable_auto_subscribe(guestip)
            # (1.2) Hypervisor subscribe physical pool which can generate limited bonus pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # (1.3) list available pools on guest, check limited bonus pool generated.
            self.check_bonus_exist(test_sku, bonus_quantity, guestip)
            # (1.4)subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)

            # (2) Check limited bonus pool will revoke after unsubscribe pool on hypervisor
            # (2.1) Unsubscribe sku on hypervisor
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
            self.hyperv_stop_guest(guest_name)
            self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
