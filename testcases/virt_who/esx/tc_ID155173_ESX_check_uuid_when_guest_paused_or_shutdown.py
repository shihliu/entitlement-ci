from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155173_ESX_check_uuid_when_guest_paused_or_shutdown(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")
            # if the below step(1,2,3) failed, the guest will can't be stop.
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)

            # (1) start a guest    
            self.esx_start_guest(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip)

            # (2)pause a guest
            self.esx_pause_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip)

            # (3)resume a guest
            self.esx_resume_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip)

            # (4)shutdown a guest
            self.esx_stop_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
