##############################################################################
## Test Description
##############################################################################
"""
Setup:

System has been successfully registered to a candlepin server.
    
Breakdown:
Actions:

1. List available Entitlement Pools via GUI

    (Refer to "List available Entitlement Pools" case)

2. Select one "Available Subscription",  then select one "Contract" entitlement pool and click "Subcribe".

3. Click "My Subscriptions" tab and check that the system is now entitled to your selected subscription.
    
Expected Results:

1. Lists available subscriptions which the machine has not subscribed to
2. no error occurs
3. your selected subscription exists in "My Subscriptions" tab page

Notes:
Unsure of what a contrat entitlement is.  Instead, just subscribe and see whether product is in my subscriptions tab.
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115175_GUI_subscribe_to_a_pool(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_in_gui(username, password)
                self.click_all_available_subscriptions_tab()
                self.click_update_button()
                subscribing = self.get_table_cell('main-window','all-subscription-table', 0, 0)
                logger.info("SUCCESS: subscribed %s" % subscribing)
                self.select_row('main-window','all-subscription-table', 0)
                self.click_button('main-window','attach-subscription')
                self.click_my_subscriptions_tab()
                subscribed = self.get_table_cell('main-window','my-subscription-table', 0, 0)
                logger.info("SUCCESS: Retrieved %s as subscribed!" % subscribed)
                if (subscribed != subscribing):
                    raise FailException("Subscription did not match what was subscribed!")
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
