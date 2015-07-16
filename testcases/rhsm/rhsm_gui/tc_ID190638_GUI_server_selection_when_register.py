from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190638_GUI_server_selection_when_register(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                samhostname = get_exported_param("SAM_HOSTNAME")
                server_url = samhostname + ":443" + "/sam/api"
                self.click_register_button()
                if self.check_server_url(server_url):
                    logger.info("It's successful to display server url %s" % server_url)
                else:
                    raise FailException("Test Faild - Failed to display server url %s" % server_url)
                self.click_dialog_next_button()
                self.input_username(username)
                self.input_password(password)
                self.check_manual_attach_checkbox()
                self.click_dialog_register_button_without_autoattach()
                if self.check_object_exist("main-window", "auto-subscribe-button") :
                    logger.info("It's successful to check auto subscribe button exist")
                else:
                    raise FailException("Test Faild - Failed to check auto subscribe button exist")
                if self.check_object_status("main-window", "register-button", "VISIBLE") == 0:
                    logger.info("It's successful to check register-button is not visible")
                else:
                    raise FailException("Test Faild - Failed to check register-button is not visible")
                if self.check_object_status("main-window", "register-menu", "VISIBLE") == 0:
                    logger.info("It's successful to check register-menu is not visible")
                else:
                    raise FailException("Test Faild - Failed to check register-menu is not visible")
                if self.check_object_status("main-window", "unregister-menu", "VISIBLE") == 1:
                    logger.info("It's successful to check unregister-menu is visible")
                else:
                    raise FailException("Test Faild - Failed to check unregister-menu is visible")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.remove_proxy()
            self.capture_image(case_name)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
