from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155146_ESX_validate_compliance_status_when_unregister_host(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")

            test_sku = VIRTWHOConstants().get_constant("productid_guest")
            bonus_quantity = VIRTWHOConstants().get_constant("guestlimit")
            sku_name = VIRTWHOConstants().get_constant("productname_guest")

            host_uuid = self.esx_get_host_uuid(destination_ip)
            
            #0).check the guest is power off or not, if power_on, stop it
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_testing_server(SAM_IP, SAM_HOSTNAME, guestip)
                self.sub_register(SAM_USER, SAM_PASS, guestip)
            # subscribe esx host with limited bonus subscription
            self.esx_subscribe_host_in_samserv(host_uuid, self.get_poolid_by_SKU(test_sku) , SAM_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # unregister the ESX host 
            self.esx_unsubscribe_all_host_in_samserv(host_uuid, SAM_IP)
            # refresh the guest
            self.sub_refresh(guestip)
            # list available subscriptions on guest
            new_available_poollist = self.sub_listavailpools(test_sku, guestip)
            if new_available_poollist != None:
                for item in range(0, len(new_available_poollist)):
                    if test_sku in new_available_poollist[item] and self.check_type_virtual(new_available_poollist[item]):
                        logger.info("listed bonus pool of product %s, but is shouldn't") % sku_name
                        self.assert_(False, case_name)
                    else:
                        logger.info("no bonus pool been list") 
            else:
                raise FailException("Failed to get available pool list from guest.")
            # list consumed subscriptions on guest
            self.sub_listconsumed(test_sku, targetmachine_ip=guestip, productexists=False)
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
