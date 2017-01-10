from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID190638_GUI_server_selection_when_register(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.open_subscription_manager()
                sever_hostname = get_exported_param("SERVER_HOSTNAME")
                server_url = "subscription.rhsm.stage.redhat.com:443/subscription"

                if self.test_server == "SAM":
                    server_url = sever_hostname + ":443/sam/api"
                elif self.test_server == "SATELLITE":
                    if "satellite" in sever_hostname:
                        sever_hostname = sever_hostname + ".novalocal"
                    server_url = sever_hostname + ":443/rhsm"

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
                # After registration, the register button disappear and auto-attach button appear
                # Check the auto-attach button in main window existance
                if self.check_object_exist("main-window", "auto-subscribe-button") :
                    logger.info("It's successful to check auto subscribe button exist")
                else:
                    raise FailException("Test Faild - Failed to check auto subscribe button exist")
                # Check the register button in main window does not exist anymore
                if self.check_element_exist("main-window", "btn", "RegisterSystem"):
                    logger.info("It's successful to check register-button in main window deos not exist anymore after registration")
                else:
                    raise FailException("Test Faild - Failed to check register-button in main window deos not exist anymore after registration")
                # The register-menu in System-drop-down is disabled after registration
                if self.check_object_status("main-window", "register-menu", "ENABLED") == 0:
                    logger.info("It's successful to check register-menu is DISABLED")
                else:
                    raise FailException("Test Faild - Failed to check register-menu is DISABLED")
                # The Unregister-menu in System-drop-down is enabled after registration
                if self.check_object_status("main-window", "unregister-menu", "ENABLED") == 1:
                    logger.info("It's successful to check unregister-menu is ENABLED")
                else:
                    raise FailException("Test Faild - Failed to check unregister-menu is enabled")
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
