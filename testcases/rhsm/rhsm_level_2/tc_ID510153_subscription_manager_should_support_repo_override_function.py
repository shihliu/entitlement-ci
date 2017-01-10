from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510153_subscription_manager_should_support_repo_override_function(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            cmd = 'subscription-manager repo-override --help'
            (ret, output) = self.runcmd(cmd, "check repo-override help message")
            if ret ==0 and 'Usage: subscription-manager repo-override [OPTIONS]' in output and 'Manage custom content repository settings' in output:
                logger.info("It's successful to check repo-override help message")
            else:
                raise FailException("Test Failed - Failed to check repo-override help message")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
