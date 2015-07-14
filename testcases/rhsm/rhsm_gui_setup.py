from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class rhsm_gui_setup(RHSMGuiBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.rhsm_gui_sys_setup()
#             self.kvm_sys_setup(get_exported_param("REMOTE_IP_2"))
#             self.kvm_setup()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
