from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID301085_VDSM_Instance_compliance_in_guest_regardless_sockets_RAM_cores(VDSMBase):
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

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4", guestip)
            # subscribe the registered guest to 1 instance pool
            poolid = self.get_pool_by_SKU(test_sku, guestip)
            self.sub_limited_subscribetopool(poolid, "1", guestip)

            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            if self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value, guestip):
                logger.info("Succeeded to check the consumed quantity value is: %s" % consumed_quantity_value)
            else:
                raise FailException("Failed to check the consumed quantity value.")

            # .check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            if self.check_installed_status(installed_status_key, installed_status_value, guestip):
                logger.info("Succeeded to check the installed Status: Subscribed")
            else:
                raise FailException("Failed to check the installed Status.")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # resume guest facts
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unsubscribe host
            self.sub_unsubscribe()
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
