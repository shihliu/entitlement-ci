##############################################################################
## Test Description
##############################################################################
"""
Setup:

Breakdown:

Actions:

1. launch subscription-manager gui and configure invalid proxy in proxy url
2. close and reopen subscription-manager gui

Expected Results:
2. subscription-manager gui should open and no error should display on console.

Notes:

"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID262134_GUI_launch_subscription_manager_gui_with_invalid_proxy_url(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                #open and save an invalid proxy url
                self.open_subscription_manager()
                self.click_register_button()
                self.click_configure_proxy_button()
                #self.check_HTTP_Proxy_checkbox()
                self.input_HTTP_proxy("invalid proxy address asdfasdf")
                self.click_save_button()
                self.click_system_registration_cancel_button()
                self.click_subscription_manager_close_button()
                #open subscription manager through cli and check for error
                self.open_subcription_manager_and_check_for_error()
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("FAILED - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            #special restore: needs to uncheck use proxy before killing program
            self.uncheck_proxy_in_subscription_manager()
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
