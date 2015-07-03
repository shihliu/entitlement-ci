from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID178186_GUI_register_with_invalid_usename_password(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                invalide_username = "invalide_username"
                invalide_password = "invalide_password"
                self.open_subscription_manager()
                self.click_register_button()
                self.click_dialog_next_button()
                self.input_username(invalide_username)
                self.input_password(invalide_password)
                self.check_manual_attach_checkbox()
                self.click_dialog_register_button_without_autoattach()
                self.check_window_exist("error-dialog")
                self.check_object_exist("error-dialog", "register-error-label")
                self.check_consumer_cert_files(exist=False)
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