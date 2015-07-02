##############################################################################
## Test Description
##############################################################################
"""
Setup:

The system has been registered
    
Breakdown:

Actions:

1. open subscription manager gui

2. go to the all available subscriptions tab and update the search

3. click on any subscriptoins with only a service_level and no service_type or that has neither
    
Expected Results:

3. "Service Level, Type" should display properly, no extra comma in the end like "Support Level, Type: Not Set, " or "Support Level, Type: Layered, "

Notes:
Completed.
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID262344_GUI_Service_level_Type_should_display_properly(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_all_available_subscriptions_tab()
                self.click_update_button()
                logger.info('Looking at Service_level of first available subscription...')
                if (self.select_row('main-window', 'all-subscription-table', 0) == -1):
                    raise FailException("Seems like you have no subscriptions!")
                service_label = self.get_label_txt('main-window','text-service-level')
                print service_label
                if service_label[-1] == ',':
                    raise FailException("FAILED: There's a comma at the end of the service_label.  Check to see if that is correct!")
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
