from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID269395_ESX_Datacenter_guest_auto_attach_bonus_pool(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")

            product_name = self.get_vw_cons("datacenter_name")
            host_sku_id = self.get_vw_cons("datacenter_sku_id")
            bonus_sku_id = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")

            host_uuid = self.esx_get_host_uuid(destination_ip)

            # 0).check the guest is power off or not on esxi host, if power on, stop it 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            # 1).check DataCenter is exist on host/hpyervisor
            host_pool_id = self.get_poolid_by_SKU(host_sku_id)
            if host_pool_id is not None or host_pool_id != "":
                logger.info("Succeeded to find the pool id of '%s': '%s'" % (host_sku_id, host_pool_id))
            else:
                raise FailException("Failed to find the pool id of %s" % host_sku_id)

            # 2).register guest to SAM/Candlepin server with same username and password
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # 3).subscribe the DataCenter subscription pool on host
            self.server_subscribe_system(host_uuid, host_pool_id, SERVER_IP)

            # 6).check the virtual pools listed on guest.
            if self.check_bonus_isExist(bonus_sku_id, bonus_quantity, guestip):
                logger.info("Succeeded to check the virtual pool exist.")
            else:
                raise FailException("Failed to check the virtual pool exist.")

            # 7).subscribe to the pool by --auto on guest 
            self.sub_auto_subscribe(guestip)

            # 8).check the consumed product on guest
            self.check_consumed_status(bonus_sku_id, "SubscriptionName", product_name, guestip)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # Unregister the ESX host 
            self.server_unsubscribe_all_system(host_uuid, SERVER_IP)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
