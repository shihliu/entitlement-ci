from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155143_validate_compliance_when_ping_pong_migrate_guest(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SAM_IP")
            SAM_HOSTNAME = get_exported_param("SAM_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")

            test_sku = VIRTWHOConstants().get_constant("productid_guest")
            bonus_quantity = VIRTWHOConstants().get_constant("guestlimit")
            sku_name = VIRTWHOConstants().get_constant("productname_guest")

            master_machine_ip = get_exported_param("REMOTE_IP")
            slave_machine_ip = get_exported_param("REMOTE_IP_2")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_host(SAM_HOSTNAME, SAM_IP, guestip)
                self.sub_register(SAM_USER, SAM_PASS, guestip)

            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_sku(test_sku, slave_machine_ip)

            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # migrate guest to slave machine
            self.vw_migrate_guest(guest_name, slave_machine_ip)
#             time.sleep(60)
            self.sub_refresh(guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # migrate guest back
            self.vw_migrate_guest(guest_name, master_machine_ip, slave_machine_ip)
#             time.sleep(60)
            # refresh the guest
            self.sub_refresh(guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip, productexists=False)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unsubscribe host
            self.sub_unsubscribe()
            self.sub_unsubscribe(slave_machine_ip)
            self.vw_stop_guests(guest_name)
            self.vw_define_guest(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
