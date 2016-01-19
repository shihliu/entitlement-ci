from utils import *
from testcases.virt_who.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17201_check_debug_function_by_config(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) enable debug mode, check debug info is exist on virt-who log.
            self.runcmd_service("stop_virtwho")
            self.config_virtwho_debug(1)
            self.vw_check_message_in_rhsm_log("%s|using libvirt as backend|DEBUG" % guestuuid, message_exists=True)

            # (2) diable debug mode, check debug info is not exist on virt-who log.
            self.runcmd_service("stop_virtwho")
            self.config_virtwho_debug(0)
            self.vw_check_message_in_rhsm_log("DEBUG|ERROR", message_exists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_virtwho_debug(1)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
