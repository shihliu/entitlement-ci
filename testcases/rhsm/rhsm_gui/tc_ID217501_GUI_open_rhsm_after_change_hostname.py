from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID217501_GUI_open_rhsm_after_change_hostname(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        bak_hostname = ""
        try:
            try:
                tmp_hostname = "hostname-temp"
                bak_hostname = self.get_hostname()
                self.set_hostname(tmp_hostname)
                self.open_subscription_manager()
                if self.check_window_open("main-window"):
                    logger.info("It's successful to open rhsm gui after change hostname")
                else:
                    raise FailException("Test Faild - Failed to open rhsm gui after change hostname")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.set_hostname(bak_hostname)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
