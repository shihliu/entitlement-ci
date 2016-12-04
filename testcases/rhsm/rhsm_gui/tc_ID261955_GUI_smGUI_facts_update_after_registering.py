##############################################################################
## Test Description
##############################################################################
"""
Setup:
subscription-manager has been installed, and be in a completely unregistered state

Breakdown:

Actions:
1. start subscription-manager-gui
2. register through the gui
3. Go to System --> View System Facts --> virt
    
Expected Results:
3. the virt info in gui should correct and consistent with it in CLI

    In the CLI during the same time:
    # subscription-manager facts --list | grep ^virt
    virt.host_type: kvm
    virt.is_guest: True
    virt.uuid: 131e448d-c000-f6bb-e2a9-8bb549e21ab4

Notes:
Completed.
"""
##############################################################################

from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class tc_ID261955_GUI_smGUI_facts_update_after_registering(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.open_subscription_manager()
                self.register_and_autosubscribe_in_gui(username, password)
                self.click_view_system_facts_menu()
                self.check_hostype_and_isguest_gui_vs_cli()
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("FAILED - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
