##############################################################################
## Test Description
##############################################################################
"""
Setup:
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
See comments in code.
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID115137_GUI_import_existing_certificates(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_my_subscriptions_tab()
                subscribed = self.get_table_cell('main-window','my-subscription-table', 0, 0)
                cert = self.generate_cert()
                self.sub_unregister()
                self.close_rhsm_gui()
                self.open_subscription_manager()
                #import certificate using new interface.  RHEL 7 changed it's search dlg and
                #the search txt box is buggy with ldtp.  We will use a system of clicks in finder
                #to search for new certificate
                self.click_import_cert_menu()
                #for RHEL 7.1, uncomment this next line and comment out the line after that line!
                #self.select_row_by_name('import-cert-dialog', 'table-places','File System')
                self.single_click_row('import-cert-dialog', 'table-places','root')
                self.double_click_row('import-cert-dialog', 'table-files','tmp')
                self.click_button('import-cert-dialog', 'import-file-button')
                if self.check_window_open("information-dialog") and self.check_object_exist("information-dialog", "import-cert-success-label"):
                    logger.info("SUCCES: Import success prompt displayed!")
                else:
                    raise FailException("FAILED: Success prompt not found!")
                #check whether imported certificate has proper productid
                productid = self.get_rhsm_cons("productid-6")
                self.check_entitlement_cert(productid)
                self.click_button('information-dialog', 'ok-button')
                self.click_my_subscriptions_tab()
                if self.get_my_subscriptions_table_my_subscriptions() == subscribed:
                    logger.info("SUCCESS: My subscription tab matches previous subscription!")
                else:
                    raise FailException("FAILED: Unable to check subscriptions under my_subscriptions tab!")
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
