##############################################################################
## Test Description
##############################################################################
"""
etup:

1.System has been successfully registered to a candlepin server.

2.Prepare an entitlement cert including a cert part ang a key part.
    
Breakdown:
Actions:

1.# subscription-manager-gui

2.Click "Import Certificate" button.

3.Chose a cert location and click "Import Certificate " button.
4.Click "My Subscriptions" bookmark.
    
Expected Results:

1.After step1, the subscription-manager GUI is opened.

2.After step2, the "Provide a Subscription Certificate" dialog pops up.

3.After step3, a prompt message "Certificate import was successful" should display.

4.After step4, the subscription binded with the imported entitlement cert should display and corresponding cert and key files should be generated in /etc/pki/entitlement/.

Notes:
When doing this test, DO NOT move the mouse or the test will fail at certain points
"""

########################################################


from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115137_GUI_import_existing_certificates(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_my_subscriptions_tab()
                subscribed = self.get_table_cell('main-window','my-subscription-table', 0, 0)
                cert = self.generate_cert()
                self.sub_unregister()
                self.close_rhsm_gui()
                self.open_subscription_manager()
                self.click_register_button()
                self.click_dialog_next_button()
                self.input_username(username)
                self.input_password(password)
                self.click_dialog_register_button()
                self.click_dialog_cancle_button()
                self.click_import_cert_menu()
                self.double_click_row('import-cert-dialog', 'table-places','File System')
                self.double_click_row('import-cert-dialog', 'table-files','tmp')
                self.double_click_row('import-cert-dialog', 'table-files','test.pem')
                if self.check_window_open("information-dialog") and self.check_object_exist("information-dialog", "import-cert-success-label"):
                    logger.info("SUCCES: Import success prompt displayed")
                else:
                    raise FailException("Test Faild - Failed to check prompt message displayed")
                # check whether entitlement certificates generated and productid in them or not
                productid = RHSMConstants().get_constant("productid")
                print productid
                self.check_entitlement_cert(productid)
                ldtp.click('dlgInformation', 'btnOK')
                self.click_my_subscriptions_tab()
                if self.get_my_subscriptions_table_my_subscriptions() == subscribed:
                    logger.info("SUCCESS: My subscription tab matches previous subscription!")
                else:
                    raise FailException("FAILED: Unable to check subscriptions under my_subscriptions tab")
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
