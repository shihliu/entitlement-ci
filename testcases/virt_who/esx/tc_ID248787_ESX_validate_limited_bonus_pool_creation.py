from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID248787_ESX_validate_limited_bonus_pool_creation(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")

            # for the RH0604852 limited pool, the sku_id is the same on host/guest
            product_name = self.get_vw_cons("productname_guest")
            host_sku_id = self.get_vw_cons("productid_guest")
            bonus_sku_id = self.get_vw_cons("productid_guest")
            bonus_quantity = self.get_vw_cons("guestlimit")

            host_uuid = self.esx_get_host_uuid(destination_ip)

            # 0).check the guest is power off or not on esxi host, if power on, stop it 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            # 1).check limited pool is exist on host/hpyervisor
            host_pool_id = self.get_poolid_by_SKU(host_sku_id)
            if host_pool_id is not None or host_pool_id != "":
                logger.info("Succeeded to find the pool id of '%s': '%s'" % (host_sku_id, host_pool_id))
            else:
                raise FailException("Failed to find the pool id of %s" % host_sku_id)

            # 2).register guest to SAM/Candlepin server with same username and password
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)

            # 3).before subscribe host, check the bonus pool is not available and the system type is Virtual 
            if self.check_bonus_exist(bonus_sku_id, bonus_quantity, guestip) is False:
                logger.info("Succeeded to check the bonus pool, no bonus bool of Virtual system type found.")
            else:
                raise FailException("Failed to check the bonus pool is exist.")

            # 4).subscribe the limited pool on host
            self.server_subscribe_system(host_uuid, host_pool_id, server_ip)

            # 5).after subscribe host, check the bonus pool's quantity is limited and system type is Virtual
            self.sub_refresh(guestip)
            if self.check_bonus_exist(bonus_sku_id, bonus_quantity, guestip) is True:
                logger.info("Succeeded to check the bonus pool quantity is: %s" % bonus_quantity)
            else:
                raise FailException("Failed to check the bonus pool quantity is exist.")

            # 6).subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(host_sku_id, guestip)

            # 7).after subscribe bonus pool on guest, there is no bonus pool listed 
            if self.check_bonus_exist(bonus_sku_id, bonus_quantity, guestip) is False:
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
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
