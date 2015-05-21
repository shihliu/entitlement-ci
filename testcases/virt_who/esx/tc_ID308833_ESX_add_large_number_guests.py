from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID308833_ESX_add_large_number_guests(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")

            guest_name = "esx_auto_guest"
            guest_total = 100
            guest_uuid_list = []

            # add 100 guests in vCenter
            for i in range(0, guest_total):
                self.esx_create_dummy_guest(guest_name + "_" + str(i), destination_ip)
                guest_uuid = self.esx_get_guest_uuid(guest_name + "_" + str(i), destination_ip)
                guest_uuid_list.append(guest_uuid)
            # check all guest uuid is in rhsm.log
            guest_uuid_list_in_log = self.get_uuid_list_in_rhsm_log()
            for i in range(0, guest_total):
                if not guest_uuid_list[i] in guest_uuid_list_in_log:
                    self.assert_(False, case_name)
                else:
                    logger.info("UUID of guest:%s exist in rhsm.log" % (guest_name + "_" + str(i)))
            # remove the 100 guests added in vCenter
            for i in range(0, guest_total):
                self.esx_remove_guest(guest_name + "_" + str(i), destination_ip)
                self.esx_destroy_guest(guest_name + "_" + str(i), destination_ip)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
