from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115139_GUI_list_available_pools(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_in_gui(username, password)
                self.click_all_available_subscriptions_tab()
                self.click_filters_button()
                self.uncheck_checkbox("filter-options-window", "match-installed-checkbox")
                self.uncheck_checkbox("filter-options-window", "match-system-checkbox")
                self.uncheck_checkbox("filter-options-window", "do-not-overlap-checkbox")
                self.click_filter_close_button()
                self.click_update_button()
                # check sub_listavailpools are all shown in gui
                productid = RHSMConstants().get_constant("productid")
                for item in self.sub_listavailpools(productid):
                    print item
                    if not self.check_content_in_all_subscription_table(item["SubscriptionName"]):
                        raise FailException("Test Faild - Failed to list %s in all-subscription-table" % item["SubscriptionName"])
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
