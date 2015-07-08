##############################################################################
## Test Description
##############################################################################
"""
Setup:
1.Prepare a subscription with a comma in the Subscription name
2.The system is registered.

Breakdown:

Actions:
1.Attach the prepared subscription
#subscription-manager attach --pool=[poolid]
2.launch subscription-manager-gui
#subscription-manager-gui
3.Look at the corresponding product in the My Installed Products tab and look at the Subscription name

Expected Results:
1.After step1 the subscription should be attached successfully
2.After step2 the rhsm gui should be launched successfully
3.After step3 Subscription should be listed with a comma in the Subscription name not an "and".

Notes:
Completed.
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID272155_GUI_subscription_name_comma_should_not_be_and(RHSMGuiBase):

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
                #look trhough the entire table and find a subscription with a comma
                for i in xrange(self.get_table_row_count('main-window','all-subscription-table')):
                    if "," in self.get_table_cell('main-window','all-subscription-table',i,0):
                        self.select_row('main-window','all-subscription-table', i)
                        old_comma_name = self.get_table_cell('main-window','all-subscription-table', i, 0)
                        self.click_button('main-window','attach-subscription')
                        break
                self.click_my_subscriptions_tab()
                sub_index = self.get_table_row_index('main-window','my-subscription-table',old_comma_name)
                if sub_index == -1:
                    raise FailException('FAILED: Unable to find the subscribed product with comma in name')
                #we found the exact name, therefore, the 'and' could not have been added in! and so we must pass!
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("FAILED - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)   
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
