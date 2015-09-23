from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID301083_Instance_one_instance_for_one_guest(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")

            test_sku = VIRTWHOConstants().get_constant("instancebase_sku_id")
            sku_name = VIRTWHOConstants().get_constant("instancebase_name")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_testing_server(SAM_IP, SAM_HOSTNAME, guestip)
                self.sub_register(SAM_USER, SAM_PASS, guestip)

            # check the instance pool Available on guest before subscribed
            instance_quantity_before = self.get_SKU_attribute(test_sku, "Available", guestip)
            # subscribe instance pool by --quantity=1 on guest  
            pool_id = self.get_poolid_by_SKU(test_sku, guestip)
            self.sub_limited_subscribetopool(pool_id, "1", guestip)
            # check the instance pool Available on guest after subscribed
            instance_quantity_after = self.get_SKU_attribute(test_sku, "Available", guestip)
            # check the result, before - after = 1
            if int(instance_quantity_before) - int(instance_quantity_after) == 1:
                logger.info("Succeeded to check, the instance quantity is right.")
            else:
                raise FailException("Failed to check, the instance quantity is not right.")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # resume guest facts
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unsubscribe host
            self.sub_unsubscribe()
            self.vw_stop_guests(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
