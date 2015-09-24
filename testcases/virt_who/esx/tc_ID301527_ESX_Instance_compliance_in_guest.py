from utils import *
from testcases.virt_who.esxbase import ESXBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID301527_ESX_Instance_compliance_in_guest(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            # for instance pool 
            sku_name = VIRTWHOConstants().get_constant("instancebase_name")
            sku_id = VIRTWHOConstants().get_constant("instancebase_sku_id")

            #0).check the guest is power off or not, if power_on, stop it
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)

            #1).register guest to SAM/Candlepin server with same username and password
            if not self.sub_isregistered(guestip):
                self.configure_testing_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            #2).subscribe instance pool by --quantity=1 on guest  
            pool_id = self.get_poolid_by_SKU(sku_id, guestip)
            self.sub_limited_subscribetopool(pool_id, "1", guestip)

            #3).check installed product status on guest, the Status should be Subscribed
            if self.check_installed_status("Status", "Subscribed", guestip):
                logger.info("Succeeded to check the installed Status: Subscribed")
            else:
                raise FailException("Failed to check the installed Status.")

            #4).check consumed subscription with Status Details: 'Subscription is current'
            if self.check_consumed_status(sku_id, "StatusDetails", "Subscription is current", guestip):
                logger.info("Succeeded to check the consumed Status Details: Subscription is current")
            else:
                raise FailException("Failed to check the consumed Status Details.")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # Unregister the ESX host 
            self.esx_unsubscribe_all_host_in_samserv(host_uuid, SERVER_IP)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
