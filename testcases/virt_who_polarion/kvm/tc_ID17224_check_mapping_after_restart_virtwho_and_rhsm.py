from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17224_check_mapping_after_restart_virtwho_and_rhsm(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) Check host/guest mapping info is exist 
            self.vw_check_uuid(guestuuid, uuidexists=True)

            # (2) Check host/guest mapping has not update after restart rhsmcert
            self.vw_start_guests(guest_name)
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd="restart_rhsmcertd")
            # (3) Check host/guest mapping info is exist after restart virt-who 
            self.vw_check_uuid(guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_stop_guests(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
