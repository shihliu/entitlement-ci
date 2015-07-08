from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID301521_Instance_host_consume_increments_instance_multiplier(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SAM_IP")
            SAM_HOSTNAME = get_exported_param("SAM_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")

            test_sku = VIRTWHOConstants().get_constant("instancebase_sku_id")
            sku_name = VIRTWHOConstants().get_constant("instancebase_name")

            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4")
            # subscribe the registered guest to 1 instance pool
            poolid = self.get_pool_by_SKU(test_sku)
            cmd = "subscription-manager subscribe --pool=%s --quantity=1" % poolid
            ret, output = self.runcmd(cmd, "Check subscribe instance with non-multiple of the instance-multiplier")
            if ret != 0 and (("is not a multiple ") or ("quantity evenly divisible by 2") in output): 
                logger.info("Succeeded to check subscribe instance with non-multiple of the instance-multiplier.")
            else:
                raise FailException("Failed to check subscribe instance with non-multiple of the instance-multiplier.")
            self.sub_limited_subscribetopool(poolid, "2")

            # check consumed subscriptions' quality, should be 2 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "2"
            if self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value):
                logger.info("Succeeded to check the consumed quantity value is: %s" % consumed_quantity_value)
            else:
                raise FailException("Failed to check the consumed quantity value.")

            # .check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Partially Subscribed"
            if self.check_installed_status(installed_status_key, installed_status_value):
                logger.info("Succeeded to check the installed Status: Partially Subscribed")
            else:
                raise FailException("Failed to check the installed Status:Partially Subscribed.")

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
