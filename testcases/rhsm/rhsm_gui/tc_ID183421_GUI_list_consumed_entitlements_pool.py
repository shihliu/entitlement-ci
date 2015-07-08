##############################################################################
## Test Description
##############################################################################
"""
Setup:
1.prepare a machine which has been registered to SAM server.

Breakdown:

Actions:

1.open the  subscription manager GUI
#subscription-manager-gui
2.click My Subscriptions to show the subscriptions which the machine has consumed

Expected Results:
1.after step1,the GUI should be opened.
2.after step 2,the consumed subscriptions should display in the table.

Notes:
Subscribes to subscriptions 1 and 3.  Be sure to have at least three available subscriptions, or
you'll get an index out of bounds error. 
Completed.
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID183421_GUI_list_consumed_entitlements(RHSMGuiBase):

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
                self.select_row('main-window','all-subscription-table', 0)
                self.click_button('main-window','attach-subscription')
                self.select_row('main-window','all-subscription-table', 1)
                self.click_button('main-window','attach-subscription')
                self.click_my_subscriptions_tab()
                #find all consumed pools in a dict
                sub_dict = self.sub_listconsumedpools()
                #go through the dictionary and dheck whether pools match
                for i in xrange(len(sub_dict)):
                    if self.get_table_cell('main-window','my-subscription-table', i, 0) != sub_dict[i]['SubscriptionName']:
                        raise FailException('FAILED: My consumed subscriptions do not match the ones listed in GUI!')
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
