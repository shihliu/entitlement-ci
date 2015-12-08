from utils import *
from testcases.virt_who.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID318873_Datacenter_socketbase_in_host(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")

            host_test_sku = self.get_vw_cons("datacenter_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")

            # Set up host facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4")

            # In host,subscribe 1 datacenter pool
            poolid = self.get_pool_by_SKU(host_test_sku)
            self.sub_limited_subscribetopool(poolid, "1")
            # In host, check consumed subscriptions' quality is 1
            self.check_consumed_status(host_test_sku, "StatusDetails", "Only supports 2 of 4 sockets.")

            # In host,subscribe 1 datacenter pool again
            self.sub_limited_subscribetopool(poolid, "1")
            # In host, check consumed subscriptions' quality is 1
            self.check_consumed_status(host_test_sku, "StatusDetails", "Subscription is current")

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
