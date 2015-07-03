##############################################################################
## Test Description
##############################################################################
"""
Setup:

1.Prepare a registered machine.
	
Breakdown:

Actions:

1.open the subscription-manager GUI

#subscription-manager-GUI

2.click  the "View System Facts" ,
3.click the  "System"
	
Expected Results:

1.after step 1, the subscription-manager GUI should be displayed
2. the Subscription-manager Facts will be displayed and the org info displays on the right panel.
3. the identity info should be displayed

Notes: 
Completed
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID178118_GUI_display_orgname_and_identity(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_view_system_facts_menu()
                self.click_facts_view_tree("system")
                self.check_org_and_id_displayed_in_facts_match(username, password)
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
