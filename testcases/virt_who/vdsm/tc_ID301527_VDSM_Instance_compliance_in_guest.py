from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID301527_VDSM_Instance_compliance_in_guest(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            test_sku = self.get_vw_cons("instancebase_sku_id")
            sku_name = self.get_vw_cons("instancebase_name")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM/Candlepin server with same username and password
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe instance pool by --quantity=1 on guest  
            pool_id = self.get_poolid_by_SKU(test_sku, guestip)
            self.sub_limited_subscribetopool(pool_id, "1", guestip)
            # check installed product status on guest, the Status should be Subscribed
            if self.check_installed_status("Status", "Subscribed", guestip):
                logger.info("Succeeded to check the installed Status: Subscribed")
            else:
                raise FailException("Failed to check the installed Status.")
            # check consumed subscription with Status Details: 'Subscription is current'
            if self.check_consumed_status(test_sku, "StatusDetails", "", guestip) or self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current", guestip):
                logger.info("Succeeded to check the consumed Status Details: Subscription is current")
            else:
                raise FailException("Failed to check the consumed Status Details.")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
