from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID284092_register_without_env_in_sam(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            org = self.get_rhsm_cons("default_org")
            cmd = "subscription-manager register --username=%s --password=%s --org=%s" % (username, password, org)
            (ret, output) = self.runcmd(cmd, "register without environments")
            if ret == 0 and ("The system has been registered with ID" in output or "The system has been registered with id" in output):
                logger.info("It's successful to verify that sam support registration without environments")
            else:
                raise FailException("Test Failed - failed to verify that sam support registration without environments")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
