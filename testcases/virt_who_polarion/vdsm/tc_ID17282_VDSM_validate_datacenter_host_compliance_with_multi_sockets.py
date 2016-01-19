from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17282_VDSM_validate_datacenter_host_compliance_with_multi_sockets(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")

            test_sku = self.get_vw_cons("datacenter_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")

            # Set up host facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4")
            poolid = self.get_pool_by_SKU(test_sku)

            #(1).subscribe host to unspecify datacenter pool
            self.sub_subscribetopool(poolid)
            # check consumed subscriptions' quality, should be 2 on host 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "2"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current")
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Not Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value)

            #(2).subscribe host to 1 datacenter pool
            self.sub_unsubscribe()
            self.sub_limited_subscribetopool(poolid, "1")
            # check consumed subscriptions' quality, should be 1 on host 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value)
            # check consumed subscription with Status Details: 'Only supports 2 of 4 sockets.'
            self.check_consumed_status(test_sku, "StatusDetails", "Only supports 2 of 4 sockets.")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # unsubscribe host
            self.sub_unsubscribe()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
