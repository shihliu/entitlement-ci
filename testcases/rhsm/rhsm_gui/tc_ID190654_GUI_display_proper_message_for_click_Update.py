from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID190654_GUI_display_proper_message_for_click_Update(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.open_subscription_manager()
                self.register_in_gui(username, password)
                self.click_all_available_subscriptions_tab()
                if self.check_object_exist("main-window", "search-subscriptions-hint-label") :
                    logger.info("It's successful to check display_proper_message_for_click_Update")
                else:
                    raise FailException("Test Faild - Failed to check display_proper_message_for_click_Update")
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