from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID190636_GUI_open_online_documentation_from_menu(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                self.open_subscription_manager()
                self.click_onlinedocumentation_menu()
                self.activate_window("onlinedocumentation-window")
                if self.check_object_exist("onlinedocumentation-window", "onlinedocumentation-window"):
                    logger.info("It's successful to check open_online_documentation_from_menu.")
                else:
                    raise FailException("Test Faild - Failed to check open_online_documentation_from_menu!")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            if self.check_window_open("security-warning-dialog"):
                self.close_window("security-warning-dialog")
            self.close_window("onlinedocumentation-window")
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()