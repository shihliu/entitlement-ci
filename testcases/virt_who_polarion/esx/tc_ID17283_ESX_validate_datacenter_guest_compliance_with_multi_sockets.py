from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17283_ESX_validate_datacenter_guest_compliance_with_multi_sockets(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)

            sku_id = self.get_vw_cons("datacenter_sku_id")
            sku_bonus_id = self.get_vw_cons("datacenter_bonus_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")
            sku_quantity = self.get_vw_cons("datacenter_bonus_quantity")

            self.setup_custom_facts("cpu.cpu_socket(s)", "4")

            # start guest
            if self.esx_guest_ispoweron(guest_name, esx_host_ip):
                self.esx_stop_guest(guest_name, esx_host_ip)
            self.esx_start_guest(guest_name, esx_host_ip)
            guestip = self.esx_get_guest_ip(guest_name, esx_host_ip)

            # register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)

            # subscribe esx host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), server_ip)
            self.check_bonus_exist(sku_bonus_id, sku_quantity, guestip)

            gpoolid = self.get_pool_by_SKU(sku_bonus_id, guestip)

            self.sub_subscribetopool(gpoolid, guestip)
            # list consumed subscriptions on the guest, should be listed
            self.sub_listconsumed(sku_name, guestip)

            self.check_consumed_status(sku_bonus_id, "QuantityUsed", "1", guestip)
            self.check_installed_status("Status", "Subscribed", guestip)

            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(gpoolid, "1", guestip)

            self.check_consumed_status(sku_bonus_id, "QuantityUsed", "1", guestip)
            self.check_installed_status("Status", "Subscribed", guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            self.esx_stop_guest(guest_name, esx_host_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
