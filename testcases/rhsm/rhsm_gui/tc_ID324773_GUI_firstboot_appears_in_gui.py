##############################################################################
## Test Description
##############################################################################
"""
Setup:
    
Breakdown:

Actions:
1. If  "/etc/sysconfig/firstboot" file exists edit "RUN_FIRSTBOOT=YES"
else  "# firstboot"  in terminal

Expected Results:
1. Firstboot should have subscription_manager register screens

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

class tc_ID324773_GUI_firstboot_appears_in_gui(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                self.restore_firstboot_environment() #as a precaution for this test
                self.open_firstboot()
                self.check_window_exist('firstboot-main-window')
                self.close_firstboot()
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("FAILED - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            #need to restore firstboot environment
            self.restore_firstboot_environment()
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
