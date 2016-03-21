from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17273_RHEVM_check_unlimited_bonus_auto_subscribe(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
#             sku_name = self.get_vw_cons("datacenter_name")
            sku_name = self.get_vw_cons("datacenter_bonus_name")

            # (1) Start guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            # (2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            self.sub_disable_auto_subscribe(guestip)
            # (3) Subscribe hypervisor
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(test_sku), server_ip)
            # (4) Guest auto subscribe
            self.sub_unsubscribe(guestip)
            self.sub_auto_subscribe(guestip)
            # (5) list consumed subscriptions on the guest, should be listed
            self.check_consumed_status(guest_bonus_sku, "SubscriptionName", sku_name, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
