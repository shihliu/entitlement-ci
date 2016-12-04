from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID332567_Need_Description_for_rhsm_debug_system_option(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Check the description of rhsm-debug MODULE-NAME
            cmd = "rhsm-debug --help | grep system"
            (ret, output) = self.runcmd(cmd, "check man page for repo-override")
            if ret == 0 and "Assemble system information as a tar file or directory" in output:
                logger.info("It's successful to Check the description of rhsm-debug MODULE-NAME.") 
            else:
                raise FailException("Test Failed - Failed to Check the description of rhsm-debug MODULE-NAME.")        
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
