from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID115141_GUI_list_products_and_subscriptions_info(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                productid = self.get_rhsm_cons("productid")
                self.click_my_installed_products_tab()
                for item in self.sub_listinstalledpools():
                    if not self.check_content_in_my_installed_products_table(item["SubscriptionName"]):
                        raise FailException("Test Faild - Failed to list %s in all-subscription-table" % item["SubscriptionName"])
                self.click_my_subscriptions_tab()
                for item in self.sub_listconsumedpools():
                    if not self.check_content_in_my_subscriptions_table(item["SubscriptionName"]):
                        raise FailException("Test Faild - Failed to list %s in my-subscription-table" % item["SubscriptionName"])
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
