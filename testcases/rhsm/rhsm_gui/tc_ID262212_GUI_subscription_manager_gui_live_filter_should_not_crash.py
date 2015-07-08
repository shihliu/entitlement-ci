##############################################################################
## Test Description
##############################################################################
"""
Setup:

Breakdown:

Actions:
1. Open subscription-manager-gui and register the system.
2. Click filters on the "All Available Subscriptions" tab, uncheck everything, and put in any string in the "Contain the text" field. After that close the filters and click 'update' to search for subscriptions.
3. Open filters again and change the text filter very quickly, and then update the search list.

Expected Results:
1. After step 1, subscription-manager-gui is loaded and regeisteration is successfull.
2. After step 2, no error happens.
3. After step 3, subscription-manager-gui should not crash.

Notes:
Does above instructions and sees whether the subscription-manager-gui window is still open
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID262212_GUI_subscription_manager_gui_live_filter_should_not_crash(RHSMGuiBase):

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
                self.uncheck_checkbox("filter-options-window", "match-system-checkbox")
                self.uncheck_checkbox("filter-options-window", "do-not-overlap-checkbox")
                self.uncheck_checkbox("filter-options-window", "match-installed-checkbox")
                #input garbage in the filter box
                self.input_text('filter-options-window','filter-subscriptions-text','testy1')
                self.click_filter_close_button()
                self.click_update_button()
                self.click_filters_button()
                #input garbage in the filter box 2nd time
                self.input_text('filter-options-window','filter-subscriptions-text','testy2')
                self.click_filter_close_button()
                self.click_update_button()
                self.check_window_exist('main-window')
            except Exception, e:
                logger.error("FAILED - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
