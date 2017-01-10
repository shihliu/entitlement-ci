from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID115147_GUI_register_and_autosubscribe(RHSMGuiBase):

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
                self.click_dialog_register_button()
                self.click_attdialog_next_button()
                self.click_dialog_subscribe_button()
                self.click_my_subscriptions_tab()
                if self.get_my_subscriptions_table_row_count() >= 1:
                    logger.info("It's successful to auto subscribe: %s" % self.get_my_subscriptions_table_my_subscriptions())
                else:
                    raise FailException("Test Faild - Failed to register and auto subscribe via GUI!")
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