from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID289138_VDSM_Datacenter_subpool_creation(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            host_test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip,host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # Check bonus pool not generated yet
            if self.check_bonus_exist(guest_bonus_sku, bonus_quantity, guestip) is False:
                logger.info("Guest isn't bonus pool before host subscribe '%s' " % sku_name)
            else:
                raise FailException("Bonus pool exist before host subscribe '%s' " % sku_name)
            # host subscribe datacenter pool
            self.sub_subscribe_sku(host_test_sku)
            # Check bonus pool has been generated after host subscribe datacenter pool
            if self.check_bonus_exist(guest_bonus_sku, bonus_quantity, guestip) is True:
                logger.info("Success to check datacenter bonus pool after host subscribe '%s' " % sku_name)
            else:
                raise FailException("Failed to check datacenter bonus pool after host subscribe '%s' " % sku_name)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unsubscribe host
            self.sub_unsubscribe()
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
