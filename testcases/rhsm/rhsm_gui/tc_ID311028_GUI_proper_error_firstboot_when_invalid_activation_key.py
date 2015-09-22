##############################################################################
# # Test Description
##############################################################################
"""
Setup:

Breakdown:

Actions:
1.firstboot -r 
2. Register using activation-key
3.Enter an invalid activation-key like 'asdf123'

    
Expected Results:
1. The firstboot GUI is opened successfully.
2. No error.
3. An alert message should be displayed saying like this:

"Couldn't find activation key 'asdf123' "

Notes:
Firstboot test specifics are included in Documentation-Ben.
Please read the note there on firstboot tests if you encounter any errors.
Completed.
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID311028_GUI_proper_error_firstboot_when_invalid_activation_key(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                if self.skip_test_on_rhel7():
                    self.assert_(True, case_name)
                else:
                    self.restore_firstboot_environment()
                    self.open_firstboot()
                    self.click_firstboot_fwd_button()
                    self.check_checkbox("firstboot-main-window", "firstboot-activationkey-checkbox")
                    self.click_firstboot_fwd_button()
                    self.input_text('firstboot-main-window', 'firstboot-organization-entry-text', 'ACME_Corporation')
                    self.input_text('firstboot-main-window', 'firstboot-activation-key-text', 'wrong')
                    self.click_firstboot_fwd_button()
                    self.check_window_exist('error-dialog')
                    self.close_firstboot()
                    self.assert_(True, case_name)
            except Exception, e:
                logger.error("FAILED - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            # need to restore firstboot environment
            self.restore_firstboot_environment()
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
