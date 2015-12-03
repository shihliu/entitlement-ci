from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID301535_VDSM_Instance_compliance_in_host(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")

            test_sku = self.get_vw_cons("instancebase_sku_id")
            sku_name = self.get_vw_cons("instancebase_name")

            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "6")
            # disable auto attach subscription
            self.sub_disable_auto_subscribe()
            # subscribe the registered host to 4 instance pool
            poolid = self.get_pool_by_SKU(test_sku)
            cmd = "subscription-manager subscribe --pool=%s --quantity=4" % poolid
            ret, output = self.runcmd(cmd, "Check subscribe instance with 4 instance")
            if ret == 0 and "Successfully" in output:
                logger.info("Succeeded to check subscribe instance with 4 instance")
                
            else:
                raise FailException("Failed to check subscribe instance with 4 instance")
            # check consumed subscriptions' quality, should be 4 on host 
            self.check_consumed_status(test_sku, "QuantityUsed", "4", "")
            # .check the Status of installed product, should be 'Partially Subscribed' status
            self.check_installed_status("Status", "Partially Subscribed")
            self.check_installed_status("StatusDetails", "Only supports 4 of 6 sockets.")

            # subscribe the registered host to 4 instance pool again
            cmd = "subscription-manager subscribe --pool=%s --quantity=2" % poolid
            ret, output = self.runcmd(cmd, "Check subscribe with 6 instance")
            if ret == 0 and "Successfully" in output:
                logger.info("Succeeded to check subscribe with 6 instance")
                
            else:
                raise FailException("Failed to check subscribe with 6 instance")
            # .check the Status of installed product, should be 'Partially Subscribed' status
            self.check_installed_status("Status", "Subscribed")
            self.check_installed_status("StatusDetails", "")

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
