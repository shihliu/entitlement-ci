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
            guest_total = 2000

            # add 2000 guests in vCenter
            for i in range(0, guest_total):
                self.esx_create_dummy_guest(guest_name + "_" + str(i), destination_ip)
                logger.info("Added dummy guest: %s" % (guest_name + "_" + str(i)))
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
