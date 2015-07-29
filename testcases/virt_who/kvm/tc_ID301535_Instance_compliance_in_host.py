from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID301535_Instance_compliance_in_host(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")

            test_sku = VIRTWHOConstants().get_constant("instancebase_sku_id")
            sku_name = VIRTWHOConstants().get_constant("instancebase_name")

            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "8")
            # subscribe the registered host to 4 instance pool
            poolid = self.get_pool_by_SKU(test_sku)
            cmd = "subscription-manager subscribe --pool=%s --quantity=4" % poolid
            ret, output = self.runcmd(cmd, "Check subscribe instance with 4 instance")
            if ret == 0 and "Successfully" in output:
                logger.info("Succeeded to check subscribe instance with 4 instance")
                
            else:
                raise FailException("Failed to check subscribe instance with 4 instance")
            # check consumed subscriptions' quality, should be 4 on host 
            if self.check_consumed_status(test_sku, "QuantityUsed", "4"):
                logger.info("Succeeded to check the consumed quantity value is 4")
            else:
                raise FailException("Failed to check the consumed quantity value is 4")

            # .check the Status of installed product, should be 'Partially Subscribed' status
            if self.check_installed_status("Status", "Partially Subscribed"):
                logger.info("Succeeded to check the installed Status: Partially Subscribed")
            else:
                raise FailException("Failed to check the installed Status is Partially Subscribed.")

            if self.check_installed_status("StatusDetails", "Only supports 4 of 8 sockets."):
                logger.info("Succeeded to check the installed Status Details: Only supports 4 of 8 sockets")
            else:
                raise FailException("Failed to check the installed Status Details: Only supports 4 of 8 sockets")

            # subscribe the registered host to 4 instance pool again
            cmd = "subscription-manager subscribe --pool=%s --quantity=4" % poolid
            ret, output = self.runcmd(cmd, "Check subscribe with 8 instance")
            if ret == 0 and "Successfully" in output:
                logger.info("Succeeded to check subscribe with 8 instance")
                
            else:
                raise FailException("Failed to check subscribe with 8 instance")

            # .check the Status of installed product, should be 'Partially Subscribed' status
            if self.check_installed_status("Status", "Subscribed"):
                logger.info("Succeeded to check the installed Status: Subscribed")
            else:
                raise FailException("Failed to check the installed Status is Subscribed.")

            if self.check_installed_status("StatusDetails", ""):
                logger.info("Succeeded to check the installed Status Details is null")
            else:
                raise FailException("Failed to check the installed Status Details is null")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # resume guest facts
            self.restore_facts()
            # unsubscribe host
            self.sub_unsubscribe()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
