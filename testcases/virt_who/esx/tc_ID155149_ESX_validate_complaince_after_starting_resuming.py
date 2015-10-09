from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID155149_ESX_validate_complaince_after_starting_resuming(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")

            test_sku = self.get_vw_cons("productid_guest")
            bonus_quantity = self.get_vw_cons("guestlimit")
            sku_name = self.get_vw_cons("productname_guest")

            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the guest is power off or not, if power_on, stop it
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # before subscribe esx host with limited subscription, need to clean all the old subscribed pool from SAM
            self.esx_unsubscribe_all_host_in_samserv(host_uuid, SERVER_IP)
            # subscribe esx host with limited bonus subscription
            self.esx_subscribe_host_in_samserv(host_uuid, self.get_poolid_by_SKU(test_sku) , SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # pause a guest by suspend from host machine.
            self.esx_pause_guest(guest_name, destination_ip)
            # resume a guest by resume from host machine.
            self.esx_resume_guest(guest_name, destination_ip)
            # refresh the guest
            self.sub_refresh(guestip)
            # List consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # shutdown a guest by shutdown from host machine.
            self.esx_stop_guest(guest_name, destination_ip)
            # start a guest by start from host machine.
            self.esx_start_guest(guest_name)
            # Refresh the guest
            self.sub_refresh(guestip)
            # List consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()


