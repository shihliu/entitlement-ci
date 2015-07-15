from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID318873_Datacenter_socketbase_in_host(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SAM_IP")
            SAM_HOSTNAME = get_exported_param("SAM_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")

            host_test_sku = VIRTWHOConstants().get_constant("datacenter_sku_id")
            sku_name = VIRTWHOConstants().get_constant("datacenter_name")

            # Set up host facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4")

            # In host,subscribe 1 datacenter pool
            poolid = self.get_pool_by_SKU(host_test_sku)
            self.sub_limited_subscribetopool(poolid, "1")
            # In host, check consumed subscriptions' quality is 1
            if self.check_consumed_status(host_test_sku, "StatusDetails", "Only supports 2 of 4 sockets."):
                logger.info("Succeeded to check host's status detail is Only supports 2 of 4 sockets ")
            else:
                raise FailException("Failed to check host's status detail is Only supports 2 of 4 sockets ")

            # In host,subscribe 1 datacenter pool again
            self.sub_limited_subscribetopool(poolid, "1")
            # In host, check consumed subscriptions' quality is 1
            if self.check_consumed_status(host_test_sku, "StatusDetails", "Subscription is current"):
                logger.info("Succeeded to check host's status detail is Subscription is current ")
            else:
                raise FailException("Failed to check host's status detail is Subscription is current ")

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
