from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID166454_subscription_manager_register_help_manual(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'subscription-manager --help'
            (ret, output) = self.runcmd(cmd, "list subscription-manager help manual!")
            if ret == 0 and ('Primary Modules' and 'Other Modules' in output):
                logger.info("Test Successful - It's successful to list subscription-manager help manual.") 
            else:
                raise FailException("Test Failed - Failed to list subscription-manager help manual.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
