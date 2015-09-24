from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155149_VDSM_validate_compliance_after_pause_shutdown(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = VIRTWHOConstants().get_constant("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = VIRTWHOConstants().get_constant("RHEVM_HOST")

            test_sku = VIRTWHOConstants().get_constant("productid_unlimited_guest")
            bonus_quantity = VIRTWHOConstants().get_constant("guestlimit_unlimited_guest")
            sku_name = VIRTWHOConstants().get_constant("productname_unlimited_guest")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip,host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku)
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
            # unsubscribe host
            self.sub_unsubscribe()
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
