from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID166455_GUI_subscription_manager_help_maual(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                self.open_subscription_manager()
                self.click_gettingstarted_menu()
                if self.check_window_open("subscription-manager-manual-window"):
                    logger.info("It's successful to check subscription_manager_help_maual.")
                else:
                    raise FailException("Test Faild - Failed to check subscription_manager_help_maual!")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.close_window("subscription-manager-manual-window")
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()