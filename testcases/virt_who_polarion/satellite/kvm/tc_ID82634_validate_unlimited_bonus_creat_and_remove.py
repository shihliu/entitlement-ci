from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID82634_validate_unlimited_bonus_creat_and_remove(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            self.runcmd_service("restart_virtwho")

            # (1) Check unlimited bonus pool will create after subscribe pool on hypervisor
            # (1.1) Start guest
            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
            # (1.2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            # (1.3) Subscribe host
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # (1.4) List available pools of guest, check related bonus pool generated.
            self.sub_listconsumed(sku_name, guestip)

            # (2) Check unlimited bonus pool will revoke after unsubscribe pool on hypervisor
            # (2.1) Unsubscribe sku on hypervisor
            self.sub_unregister()
            # (2.2) Check consumed bonus pool revoke on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.vw_stop_guests(guest_name)
            # register host
            self.sub_register(server_user, server_pass)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
