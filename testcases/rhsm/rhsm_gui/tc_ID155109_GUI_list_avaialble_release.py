##############################################################################
## Test Description
##############################################################################
"""
Setup:

1. The system is registered and autosubscribed.
    
Breakdown:
Actions:

1. Open subscription-manager-gui.

2. Click "System Preferences" button in toolbar.

3. Check the drop-down list of release version.
    
Expected Results:

1. After step1, subscription manager GUI is openned.

2. After step2, "System Preferences" dialog should display.

3. After step3, release list should display.

Notes:
Completed
"""

########################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID155109_GUI_list_avaialble_release(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_preferences_menu()
                for item in self.get_available_release():
                    if self.check_combo_item("system-preferences-dialog", "release-version-combobox", item):
                        logger.info("SUCCESS: Checked release %s exist." % item)
                    else:
                        raise FailException("FAILED: Unable to check release %s exist." % item)
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
