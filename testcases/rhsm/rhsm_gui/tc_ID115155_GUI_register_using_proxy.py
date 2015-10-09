##############################################################################
## Test Description
##############################################################################
"""
Setup:
1.Prepare a proxy with its location, username and password.
2.proxy address is : squid.corp.redhat.com:3128

Breakdown:

Actions:

1.# subscription-manager-gui
2.Click "Proxy Configuration" button.
3.Input "Proxy Location", "Proxy Username" and "Proxy Password" and click "close" button.
4.Click "Register" button.
5.Input "Login", "Password" and "System Name" and click "Register" button.

Expected Results:
1.After step1, the subscription-manager GUI is opened.
2.After step2, the "Advanced Network Configuration" dialog pops up.
3.No error prompts.
4.After step4, the "system registration" dialog pops up.
5.After step5, registration succeeds and the following certs are dropped into /etc/pki/consumer: cert.pem, key.pem.

Notes:
Completed.
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID115155_GUI_register_using_proxy(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.open_subscription_manager()
                self.check_consumer_cert_files(exist=False)
                self.click_register_button()
                self.click_configure_proxy_button()
                self.check_HTTP_proxy_checkbox()
                self.input_HTTP_proxy("squid.corp.redhat.com:3128")
                self.click_proxy_close_button()
                self.click_dialog_next_button()
                self.input_username(username)
                self.input_password(password)
                self.check_manual_attach_checkbox()
                self.click_dialog_register_button_without_autoattach()
                self.check_consumer_cert_files(exist=True)
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
