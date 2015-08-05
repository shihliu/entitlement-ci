##############################################################################
## Test Description
##############################################################################
"""
Setup:
System has been successfully subscribed to some products.

Breakdown:

Actions:
1. Open subscription-manager-gui
2. Click "My Subscriptions" tab
3. Select a subscription and click "Unsubscribe" button
4. Repeat step 3 for all consumed subscriptions

Expected Results:
1. "Subscription Manager" dialog pops up.
2. All subscriptions consumed by this machine are listed
3. The selected subscription is unsubscribed
4. All subscriptions are unsubscribed

Note: 
Checks to see whether unsubscribed products are not in the list anymore.
Simple timer installed in case while loops does not end.
Completed.
"""
##############################################################################

from utils import *
import time
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115179_GUI_unsubscribe_from_products(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_tab('my-subscriptions')
                timeout = time.time() + 120 #2 min timer
                while self.get_table_row_count('main-window','my-subscription-table') > 0:
                    if time.time() > timeout: raise FailException("unsubscription process timed out!")
                    self.click_button('main-window', 'remove-subscriptions-button')
                    self.check_window_exist('question-dialog')
                    self.click_button('question-dialog', 'yes-button')
                    logger.info("SUCCESS: Unsubscribed from a product!")
                logger.info("SUCCESS: Unsubscribed from all products!")
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
