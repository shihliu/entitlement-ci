from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID155149_RHEVM_validate_compliance_after_pause_shutdown(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip,hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # subscribe the hypervsior to the physical pool which can generate bonus pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(test_sku),SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (1)pause a guest
            self.rhevm_pause_vm(guest_name, rhevm_ip)
            # (2)resume a guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # Check consumed subscriptions on guest
            self.check_consumed_status(test_sku, "SubscriptionName", sku_name, guestip)
            # (3)shutdown a guest
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # (4)start a guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # Check consumed subscriptions on guest
            self.check_consumed_status(test_sku, "SubscriptionName", sku_name, guestip)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unregister the hypervisor
            self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
