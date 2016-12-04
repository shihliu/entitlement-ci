from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509762_check_usage_statement_of_rhsm_icon(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = "rhsm-icon --help | grep -B1 rhsm-icon"
            (ret, output) = self.runcmd(cmd, "check rhsm-icon help")
            if ret == 0 and 'rhsm-icon [OPTION...]' in output:
                logger.info("It's successful to check rhsm-icon help")
            else:
                raise FailException("Test Failed - Failed to check rhsm-icon help")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
