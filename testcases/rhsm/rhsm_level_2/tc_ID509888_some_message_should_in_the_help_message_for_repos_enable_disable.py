from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509888_some_message_should_in_the_help_message_for_repos_enable_disable(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
#            username = self.get_rhsm_cons("username")
#            password = self.get_rhsm_cons("password")
#            self.sub_register(username, password)
#            autosubprod = self.get_rhsm_cons("autosubprod")
#            self.sub_autosubscribe(autosubprod)
            cmd = "subscription-manager repos --help"
            (ret, output) = self.runcmd(cmd, "run repos --help")
            if ret == 0 and ("repository to enable (can be specified more than" in output) and ("repository to disable (can be specified more than" in output):
                logger.info("message is in the repos --help")
            else:
                raise FailException("Test Failed - message is not in the repos --help")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
