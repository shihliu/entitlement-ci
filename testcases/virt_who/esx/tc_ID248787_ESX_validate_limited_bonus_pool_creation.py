from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID248787_ESX_validate_limited_bonus_pool_creation(VIRTWHOBase):
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

            # for the RH0604852 limited pool, the sku_id is the same on host/guest
            product_name = VIRTWHOConstants().get_constant("productname_guest")
            host_sku_id = VIRTWHOConstants().get_constant("productid_guest")
            bonus_sku_id = VIRTWHOConstants().get_constant("productid_guest")
            bonus_quantity = VIRTWHOConstants().get_constant("guestlimit")

            host_uuid = self.esx_get_host_uuid(destination_ip)
            
            #0).check the guest is power off or not on esxi host, if power on, stop it 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1).check limited pool is exist on host/hpyervisor
            host_pool_id = self.get_poolid_by_SKU(host_sku_id)
            if host_pool_id is not None or host_pool_id !="":
                 logger.info("Succeeded to find the pool id of '%s': '%s'" % (host_sku_id, host_pool_id))
            else:
                raise FailException("Failed to find the pool id of %s" % host_sku_id)

            #2).register guest to SAM/Candlepin server with same username and password
            if not self.sub_isregistered(guestip):
                self.configure_testing_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SAM_USER, SAM_PASS, guestip)

            #3).before subscribe host, check the bonus pool is not available and the system type is Virtual 
            if self.check_bonus_isExist(bonus_sku_id, bonus_quantity, guestip) is False:
                logger.info("Succeeded to check the bonus pool, no bonus bool of Virtual system type found.")
            else:
                raise FailException("Failed to check the bonus pool is exist.")

            #4).subscribe the limited pool on host
            self.esx_subscribe_host_in_samserv(host_uuid, host_pool_id, SAM_IP)

            #5).after subscribe host, check the bonus pool's quantity is limited and system type is Virtual
            self.sub_refresh(guestip)
            if self.check_bonus_isExist(bonus_sku_id, bonus_quantity, guestip) is True:
                logger.info("Succeeded to check the bonus pool quantity is: %s" % bonus_quantity)
            else:
                raise FailException("Failed to check the bonus pool quantity is exist.")

            #6).return the bonus pool id for subscribe 
            poollist = self.sub_listavailpools(bonus_sku_id, guestip)
            if poollist != None:
                for item in range(0, len(poollist)):
                    if "Available" in poollist[item]:
                        SKU_Number = "Available"
                    else:
                        SKU_Number = "Quantity"
                    if poollist[item]["SKU"] == bonus_sku_id and self.check_type_virtual(poollist[item]) and poollist[item][SKU_Number] == bonus_quantity:
                        bonus_pool_id = poollist[item]["PoolID"]
                        self.sub_subscribetopool(bonus_pool_id, guestip)
            else:
                raise FailException("Failed to get available pool list from guest.")

            #7).after subscribe bonus pool on guest, there is no bonus pool listed 
            if self.check_bonus_isExist(bonus_sku_id, bonus_quantity, guestip) is False:
                logger.info("Succeeded to check the bonus pool, no bonus bool of Virtual system type found.")
            else:
                raise FailException("Failed to check the bonus pool exist.")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # Unregister the ESX host 
            self.esx_unsubscribe_all_host_in_samserv(host_uuid, SAM_IP)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
