##############################################################################
## Test Description
##############################################################################
"""
Setup:
	
Breakdown:

Actions:

1.remove the CA file

#mv /etc/rhsm/ca/* /root/tmp

2.launch rhsm gui

#subscription-manager-gui
	
Expected Results:

1.After step2 the rhsm gui should be launched successfully.

Notes:
Completed.
"""
##############################################################################
from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID272161_GUI_rhsm_gui_should_launch_although_CA_cert_invalid(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                self.move_ca_to_tmp()
                logger.info("SUCCESS: Moved CA to tmp")
                self.open_subscription_manager()
                logger.info("SUCCESS: Opened sm-gui without crashing!")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)   
            #need to move CA back or else uregister will fail for any following tests!
            self.move_ca_back()
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
