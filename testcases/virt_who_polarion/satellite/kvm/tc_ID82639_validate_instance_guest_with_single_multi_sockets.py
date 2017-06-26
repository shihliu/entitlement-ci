from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID82639_validate_instance_guest_with_single_multi_sockets(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            test_sku = self.get_vw_cons("instancebase_sku_id")
            sku_name = self.get_vw_cons("instancebase_name")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # (1) Check guest with one sockets
            # (1.1) Set up guest socket to 1
            self.setup_custom_facts("cpu.cpu_socket(s)", "1")
            poolid = self.get_pool_by_SKU(test_sku, guestip)
            # (1.2) Subscribe guest to unspecify instance pool
            # check the instance pool Available on guest before subscribed
            instance_quantity_before = self.get_SKU_attribute(test_sku, "Available", guestip)
            self.sub_subscribetopool(poolid, guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
            # check the instance pool Available on guest after subscribed
            instance_quantity_after = self.get_SKU_attribute(test_sku, "Available", guestip)
            # check the result, before - after = 1
            if int(instance_quantity_before) - int(instance_quantity_after) == 1:
                logger.info("Succeeded to check, the instance quantity is right.")
            else:
                raise FailException("Failed to check, the instance quantity is not right.")
           # (1.3) Subscribe guest to 2 instance pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(poolid, "2", guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current", guestip)

            # (2) Check guest with multi sockets
            self.sub_unsubscribe(guestip)
            # (2.1) Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "8", guestip)
            poolid = self.get_pool_by_SKU(test_sku, guestip)
            # (2.2) Subscribe guest to unspecify instance pool
            self.sub_subscribetopool(poolid, guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
            # (2.3) Subscribe guest to 1 instance pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(poolid, "1", guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current", guestip)
            # (2.4) Subscribe guest to 6 instance pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(poolid, "6", guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)

            # (3) Check host with one sockets
            # Set up host socket to 1
            self.setup_custom_facts("cpu.cpu_socket(s)", "1")
            poolid = self.get_pool_by_SKU(test_sku)
            # (3.1).subscribe host to unspecify instance pool
            self.sub_subscribetopool(poolid)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "2"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current")
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value)
            # (3.2).subscribe host to 1 instance pool
            self.sub_unsubscribe()
            cmd = "subscription-manager subscribe --pool=%s --quantity=1" % poolid
            ret, output = self.runcmd(cmd, "Check subscribe instance with non-multiple of the instance-multiplier")
            if ret != 0 and (("is not a multiple ") or ("quantity evenly divisible by 2") in output): 
                logger.info("Succeeded to check subscribe instance with non-multiple of the instance-multiplier.")
            else:
                raise FailException("Failed to check subscribe instance with non-multiple of the instance-multiplier.")
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Not Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value)

            # (4) Check host with multi sockets
            self.setup_custom_facts("cpu.cpu_socket(s)", "8")
            poolid = self.get_pool_by_SKU(test_sku)
            # (4.1).subscribe host to unspecify instance pool
            self.sub_unsubscribe()
            self.sub_subscribetopool(poolid)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "8"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current")
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value)
            # (4.2).subscribe host to 1 instance pool
            self.sub_unsubscribe()
            cmd = "subscription-manager subscribe --pool=%s --quantity=1" % poolid
            ret, output = self.runcmd(cmd, "Check subscribe instance with non-multiple of the instance-multiplier")
            if ret != 0 and (("is not a multiple ") or ("quantity evenly divisible by 2") in output): 
                logger.info("Succeeded to check subscribe instance with non-multiple of the instance-multiplier.")
            else:
                raise FailException("Failed to check subscribe instance with non-multiple of the instance-multiplier.")
            # (4.3).subscribe host to 2 instance pool
            self.sub_unsubscribe()
            self.sub_limited_subscribetopool(poolid, "2")
            # check consumed subscriptions' quality, should be 2 on host 
            self.check_consumed_status(test_sku, "QuantityUsed", "2")
            # .check the Status of installed product, should be 'Partially Subscribed' status
            self.check_installed_status("Status", "Partially Subscribed")
            self.check_installed_status("StatusDetails", "Only supports 2 of 8 sockets.")
            # (4.4).Auto subscribe host
            self.sub_auto_subscribe()
            # .check the Status of installed product, should be 'Subscribed' status
            self.check_installed_status("Status", "Subscribed")
            self.check_installed_status("StatusDetails", "")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.vw_stop_guests(guest_name)
#             self.restore_facts()
            self.sub_unsubscribe()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
