from utils import *
from testcases.virt_who.esxbase import ESXBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID289216_ESX_Datacenter_1_subscription_sufficient_to_guest(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")

            product_name = VIRTWHOConstants().get_constant("datacenter_name")
            host_sku_id = VIRTWHOConstants().get_constant("datacenter_sku_id")
            bonus_sku_id = VIRTWHOConstants().get_constant("datacenter_bonus_sku_id")
            bonus_quantity = VIRTWHOConstants().get_constant("datacenter_bonus_quantity")

            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the guest is power off or not, if power_on, stop it
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)

            #1).check DataCenter is exist on host/hpyervisor
            host_pool_id = self.get_poolid_by_SKU(host_sku_id)
            if host_pool_id is not None or host_pool_id !="":
                 logger.info("Succeeded to find the pool id of '%s': '%s'" % (host_sku_id, host_pool_id))
            else:
                raise FailException("Failed to find the pool id of %s" % host_sku_id)

            #2).register guest to SAM/Candlepin server with same username and password
            if not self.sub_isregistered(guestip):
                self.configure_testing_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            #3).set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4", guestip)

            #4).subscribe the DataCenter subscription pool on host
            self.esx_subscribe_host_in_samserv(host_uuid, host_pool_id, SERVER_IP)

            #5).for esxi hypervisor, skip to check the consumed status details

            #6).check the bonus pool is available and quantity is unlimited
            if self.check_bonus_isExist(bonus_sku_id, bonus_quantity, guestip) is True:
                logger.info("Succeeded to check the bonus pool quantity is: %s" % bonus_quantity)
            else:
                raise FailException("Failed to check the bonus pool quantity.")
            
            #7).subscribe to the bonus pool. 
            self.sub_subscribe_sku(bonus_sku_id, guestip)

            #8).check the Status Details of consumed product
            consumed_status_key = "StatusDetails"
            consumed_status_value = "Subscription is current"
            if self.check_consumed_status(bonus_sku_id, consumed_status_key, consumed_status_value, guestip):
                logger.info("Succeeded to check the consumed Status Details: Subscription is current")
            else:
                raise FailException("Failed to check the consumed Status Details.")

            #9).check the Status of installed product
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
            if guestip != None and guestip != "":
                self.restore_facts(guestip)
                self.sub_unregister(guestip)
            # Unregister the ESX host 
            self.esx_unsubscribe_all_host_in_samserv(host_uuid, SERVER_IP)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
