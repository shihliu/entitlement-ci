##############################################################################
## Test Description
##############################################################################
"""
Setup:
1. subscription-manager-gui is already running and it either minimized or in the background.

Breakdown:

Actions:
1. Open another terminal and run subscription-manager-gui on the terminal.

Expected Results:
1. After step 1, the subscription-manager-gui window is brought to foreground, and the following message is displayed:
# subscription-manager-gui
subscription-manager-gui is already running

Notes:
Completed.
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID261838_GUI_smGUI_on_terminal_when_running_smGUI(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                self.open_subscription_manager_first()
                if not(self.open_subscription_manager_by_cmd_check_output()):
                    FailException("FAILED: Error when opening subscription manager twice or error message wrong!")
                logger.info("SUCCESS: Opened sm-gui on terminal without crashing!")
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
