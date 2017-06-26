from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17286_validate_limited_bonus_pool_creation(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")

            test_sku = self.get_vw_cons("productid_guest")
            bonus_quantity = self.get_vw_cons("guestlimit")
            sku_name = self.get_vw_cons("productname_guest")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
            self.runcmd_service("restart_virtwho")

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            self.sub_subscribe_sku(test_sku)

            #(1). List available pools on guest, check related bonus pool generated.
            self.check_bonus_exist(test_sku, bonus_quantity, guestip)

            #(2). Subscribe the registered guest to the corresponding bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # unsubscribe host
            self.sub_unsubscribe()
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.vw_stop_guests(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
