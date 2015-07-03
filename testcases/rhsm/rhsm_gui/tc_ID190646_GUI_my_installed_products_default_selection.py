##############################################################################
## Test Description
##############################################################################
"""
Setup:

1.prepare a machine which has been registered to SAM/candlepin server

Breakdown:

Actions:

1.open the subscription manager GUI

#subscription-manager-gui

2.check whether the first entry  in the My Installed Products table is selected as default

Expected Results:

1. after step 1, the GUI should be opened

2.the first entry should be selected and more infomation should be displayed below the table.

Notes:
Completed.
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190646_GUI_my_installed_products_default_selection(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                default_info_label = self.get_text_from_txtbox('main-window','text-product')
                default_name = self.get_table_cell('main-window','installed-product-table', 0, 0)
                if default_info_label != default_name:
                    raise FailException('FAILED: First row in my-subscriptions is NOT default selection and infobox')
                logger.info("SUCCESS: Default selection works!")
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
