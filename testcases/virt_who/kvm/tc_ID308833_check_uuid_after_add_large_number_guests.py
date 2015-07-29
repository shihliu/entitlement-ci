from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID308833_check_uuid_after_add_large_number_guests(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_path = VIRTWHOConstants().get_constant("nfs_image_path")
            guest_name = "kvm_auto_guest"
            guest_total = 100
            guest_uuid_list = []

            # add 100 guests in vCenter
            for i in range(0, guest_total):
                self.define_vm(guest_name + "_" + str(i), guest_path)
                guest_uuid = self.vw_get_uuid(guest_name + "_" + str(i))
                guest_uuid_list.append(guest_uuid)
            # check all guest uuid is in rhsm.log
            guest_uuid_list_in_log = self.get_uuid_list_in_rhsm_log(logger)
            for i in range(0, guest_total):
                if not guest_uuid_list[i] in guest_uuid_list_in_log:
                    raise FailException("Failed to check UUID of guest:%s exist in rhsm.log" % (guest_name + "_" + str(i)))
                else:
                    logger.info("UUID of guest:%s exist in rhsm.log" % (guest_name + "_" + str(i)))

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # whatever happened, remove the 100 guests added in vCenter
            for i in range(0, guest_total):
                self.vw_undefine_guest(guest_name + "_" + str(i))
            # self.shutdown_vm(guest_name)
            self.vw_define_all_guests()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

