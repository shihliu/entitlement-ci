from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190656_GUI_two_filter_options_enabled_by_default(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_in_gui(username, password)
                self.click_all_available_subscriptions_tab()
                self.click_filters_button()
                if self.verifycheck_checkbox("filter-options-window", "match-system-checkbox") and self.verifycheck_checkbox("filter-options-window", "do-not-overlap-checkbox"):
                    logger.info("It's successful to check two_filter_options_enabled_by_default")
                else:
                    raise FailException("Test Faild - Failed to check two_filter_options_enabled_by_default")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()