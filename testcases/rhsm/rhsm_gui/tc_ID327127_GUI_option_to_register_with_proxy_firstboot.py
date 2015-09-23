##############################################################################
# # Test Description
##############################################################################
"""
Setup:
    
Breakdown:

Actions:

1. Start Firstboot 
2. click Next goes to the subscription-manager-firstboot page.

Expected Results:

1.After step2 There should be an option to register with proxy

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

class tc_ID327127_GUI_option_to_register_with_proxy_firstboot(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        if not self.skip_on_rhel7():
            try:
                try:
                    self.restore_firstboot_environment()
                    self.open_firstboot()
                    self.click_firstboot_fwd_button()
                    self.check_object_exist('firstboot-main-window', 'configure-proxy-button')
                    self.close_firstboot()
                    self.assert_(True, case_name)
                except Exception, e:
                    logger.error("Test Failed - ERROR Message:" + str(e))
                    self.assert_(False, case_name)
            finally:
                self.capture_image(case_name)
                # need to restore firstboot environment
                self.restore_firstboot_environment()
                self.restore_gui_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
