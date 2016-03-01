from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17224_HYPERV_check_mapping_after_restart_virtwho_and_rhsm(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            guestuuid = self.hyperv_get_guest_guid(guest_name)
            hostuuid = self.hyperv_get_host_uuid()

            # (1) Check host/guest mapping info is exist 
            self.hypervisor_check_uuid(hostuuid, guestuuid)
            # (2) Check host/guest mapping has not update after restart rhsmcert
            self.hyperv_start_guest(guest_name)
            self.vw_check_message_in_rhsm_log(guestuuid, checkcmd="service rhsmcertd restart")
            # (3) Check host/guest mapping info is exist after restart virt-who 
            self.hypervisor_check_uuid(hostuuid, guestuuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.hyperv_stop_guest(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
