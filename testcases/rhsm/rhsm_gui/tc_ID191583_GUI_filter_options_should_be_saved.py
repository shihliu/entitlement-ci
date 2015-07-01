##############################################################################
## Test Description
##############################################################################
"""
Setup:

System has been registered.
	
Breakdown:

Actions:

1. Launch the subscription-manager GUI
#subscription-manager-gui
2. Click the "All Available Subscriptions"
3. Click the "Filters" button, and remeber the current filters,
4. Alter the filters
5. Close the "Filters"
6. Reopen "Filters"
	
Expected Results:

1. Display the subscription-manager GUI
2. Give the prompt: "Press Update to search for subscriptions." 
3. Display the current filters
4. Alter the filters successfully
5. "Filters" dialog closed
6. The current filters are same with step4

Notes:
Completed
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID272161_GUI_filter_options_should_be_saved(RHSMGuiBase):

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
                self.check_checkbox("filter-options-window", "match-installed-checkbox")
                self.uncheck_checkbox("filter-options-window", "match-system-checkbox")
                self.uncheck_checkbox("filter-options-window", "do-not-overlap-checkbox")
                
                #input garbage in the filter box
                self.input_text('filter-options-window','filter-subscriptions-text','This is testy-test-mactest') 
                self.click_filter_close_button()
                self.click_filters_button()

                if (not(self.verifycheck_checkbox("filter-options-window", "match-installed-checkbox") and 
                   not(self.verifycheck_checkbox("filter-options-window", "match-system-checkbox")) and
                   not(self.verifycheck_checkbox("filter-options-window", "do-not-overlap-checkbox"))) and
                   self.get_text_from_txtbox("filter-options-window","filter-subscriptions-text") == 'This is testy-test-mactest'):
                  raise FailException("FAILED: Filter settings not saved!")

            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
