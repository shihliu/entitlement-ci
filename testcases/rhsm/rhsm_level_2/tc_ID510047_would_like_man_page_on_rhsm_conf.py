from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510047_would_like_man_page_on_rhsm_conf(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'man -f rhsm.conf'
            (ret, output) = self.runcmd(cmd, "check rhsm.conf manpage")
            if ret ==0 and ('rhsm.conf (5)        - Configuration file for the subscription-manager tooling' in output or 'rhsm.conf [rhsm]     (5)  - Configuration file for the subscription-manager tooling' in output):
                logger.info("It's successful to check rhsm.conf manpage")
            else:
                raise FailException("Test Failed - Failed to check rhsm.conf manpage")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
