from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID289221_ESX_Datacenter_guest_revoke_when_unregister_host(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")

            product_name = self.get_vw_cons("datacenter_name")
            host_sku_id = self.get_vw_cons("datacenter_sku_id")
            bonus_sku_id = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")

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
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            #3).subscribe the DataCenter subscription pool on host
            self.esx_subscribe_host_in_samserv(host_uuid, host_pool_id, SERVER_IP)

            #4).check the bonus pool is available and quantity is unlimited
            if self.check_bonus_isExist(bonus_sku_id, bonus_quantity, guestip) is True:
                logger.info("Succeeded to check the bonus pool quantity is: %s" % bonus_quantity)
            else:
                raise FailException("Failed to check the bonus pool.")
            
            #5).subscribe to the bonus pool. 
            self.sub_subscribe_sku(bonus_sku_id, guestip)

            #6). list consumed subscriptions on the guest, should be listed
            self.sub_listconsumed(product_name, guestip)

            #7). unregister host from SAM server.
            self.esx_unsubscribe_all_host_in_samserv(host_uuid, SERVER_IP)

            #8). refresh on the guest 
            self.sub_refresh(guestip)

            #9). check bonus pool is revoked on guest
            if self.check_bonus_isExist(bonus_sku_id, bonus_quantity, guestip) is False:
                logger.info("Succeeded to check, the bonus pool is revoked.")
            else:
                raise FailException("Failed to check, the bonus pool is not revoked.")

            #10). list consumed subscriptions on the guest, should be revoked
            if self.check_consumed_status(bonus_sku_id, guestip) is False:
                logger.info("Succeeded to check the consumed pool, no consumed pool displayed for %s " % bonus_sku_id)
            else:
                raise FailException("Failed to check the consumed pool, should be revoked.")

            #11).check the Status of installed product, should be "Not Subscribed"
            installed_status_key = "Status"
            installed_status_value = "Not Subscribed"
            if self.check_installed_status(installed_status_key, installed_status_value, guestip):
                logger.info("Succeeded to check the installed Status: %s" %installed_status_value)
            else:
                raise FailException("Failed to check the installed Status.")

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
