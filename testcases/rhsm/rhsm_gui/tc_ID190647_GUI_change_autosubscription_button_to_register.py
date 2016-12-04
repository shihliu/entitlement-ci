from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID190647_GUI_change_autosubscription_button_to_register(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.open_subscription_manager()
                self.click_register_button()
                self.click_dialog_next_button()
                self.input_username(username)
                self.input_password(password)
                self.check_manual_attach_checkbox()
                self.click_dialog_register_button_without_autoattach()
                if self.check_object_exist("main-window", "auto-subscribe-button") :
                    logger.info("It's successful to check auto subscribe button exist")
                else:
                    raise FailException("Test Faild - Failed to check auto subscribe button exist")
                self.click_autoattach_button()
                self.click_unregister_menu()
                if self.check_object_status("main-window", "auto-subscribe-button", "VISIBLE") == 0:
                    logger.info("It's successful to check auto-subscribe-button is not visible")
                else:
                    raise FailException("Test Faild - Failed to check auto-subscribe-button is not visible")
                
                if self.check_object_status("main-window", "register-button", "VISIBLE") == 1:
                    logger.info("It's successful to check register-button is visible")
                else:
                    raise FailException("Test Faild - Failed to check register-button is visible")
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

