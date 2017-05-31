from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID82636_validate_dc_host_vdc_guest_multi_sockets(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            host_test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            # Set up host facts to 4
            self.setup_custom_facts("cpu.cpu_socket(s)", "4")
            poolid = self.get_pool_by_SKU(host_test_sku)

            self.runcmd_service("restart_virtwho")
            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
            
            # (1) check multi-sockets host subscribe DC
            # (1.1) Subscribe host to unspecify datacenter pool
            self.sub_disable_auto_subscribe()
            self.sub_unsubscribe()
            self.sub_subscribetopool(poolid)
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "2"
            self.check_consumed_status(host_test_sku, consumed_quantity_key, consumed_quantity_value)
            # (1.2)check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(host_test_sku, "StatusDetails", "Subscription is current")
            # (1.3)check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Not Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value)
            # (1.4).subscribe host to 1 datacenter pool
            self.sub_unsubscribe()
            self.sub_limited_subscribetopool(poolid, "1")
            # (1.5)check consumed subscriptions' quality, should be 1 on host 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(host_test_sku, consumed_quantity_key, consumed_quantity_value)
            # (1.6)check consumed subscription with Status Details: 'Only supports 2 of 4 sockets.'
            self.check_consumed_status(host_test_sku, "StatusDetails", "Only supports 2 of 4 sockets.")

            # (2) Check multi-sockets guest subscribe DC
            # (2.1).subscribe guest to unspecify datacenter pool
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            gpoolid = self.get_pool_by_SKU(guest_bonus_sku, guestip)
            self.sub_subscribetopool(gpoolid, guestip)
            # (2.2)check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # (2.3)check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(guest_bonus_sku, "StatusDetails", "Subscription is current", guestip)
            # (2.4)check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
            # (2.5).subscribe the registered guest to 1 bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(gpoolid, "1", guestip)
            # (2.6)check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # (2.7)check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # unsubscribe all subscriptions on  hypervisor
            self.sub_unsubscribe()
            self.restore_facts()
            # resume guest facts
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.vw_stop_guests(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
