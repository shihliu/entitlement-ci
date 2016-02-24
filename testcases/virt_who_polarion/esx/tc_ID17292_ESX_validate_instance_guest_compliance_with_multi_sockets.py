from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17292_ESX_validate_instance_guest_compliance_with_multi_sockets(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)

            sku_id = self.get_vw_cons("instancebase_sku_id")
            sku_name = self.get_vw_cons("instancebase_name")

            # start guest
            if self.esx_guest_ispoweron(guest_name, esx_host_ip):
                self.esx_stop_guest(guest_name, esx_host_ip)
            self.esx_start_guest(guest_name, esx_host_ip)
            guestip = self.esx_get_guest_ip(guest_name, esx_host_ip)

            # register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)

            self.setup_custom_facts("cpu.cpu_socket(s)", "8")
            poolid = self.get_pool_by_SKU(sku_id, guestip)

            self.sub_subscribetopool(poolid, guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            self.check_consumed_status(sku_id, "QuantityUsed", "1", guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(sku_id, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            self.check_installed_status("Status", "Subscribed", guestip)

            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(poolid, "1", guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            self.check_consumed_status(sku_id, "QuantityUsed", "1", guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(sku_id, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            self.check_installed_status("Status", "Subscribed", guestip)

            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(poolid, "2", guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(sku_id, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            self.check_installed_status("Status", "Subscribed", guestip)

            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(poolid, "6", guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(sku_id, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            self.check_installed_status("Status", "Subscribed", guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # resume guest facts
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.hyperv_stop_guest(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
