from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155149_ESX_validate_complaince_after_starting_resuming(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SAM_IP")
            SAM_HOSTNAME = get_exported_param("SAM_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")

            test_sku = VIRTWHOConstants().get_constant("productid_guest")
            bonus_quantity = VIRTWHOConstants().get_constant("guestlimit")
            sku_name = VIRTWHOConstants().get_constant("productname_guest")

            host_uuid = self.esx_get_host_uuid(destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_host(SAM_HOSTNAME, SAM_IP, guestip)
                self.sub_register(SAM_USER, SAM_PASS, guestip)
            # subscribe esx host with limited bonus subscription
            self.esx_subscribe_host_in_samserv(host_uuid, self.get_poolid_by_SKU(test_sku) , SAM_IP)
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


