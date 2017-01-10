from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510089_yum_subscription_manager_plugin_will_not_put_non_error_information_on_stderr(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.check_and_backup_yum_repos()
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # Check non-error information not on stderr
            cmd = 'yum repolist 2> f2 > f1; cat f2'
            (ret, output) = self.runcmd(cmd, "check non-error information not on stderr")
            if ret ==0 and output.strip() == '':
                logger.info("It's successful to check non-error information not on stderr")
            else:
                raise FailException("Test Failed - Failed to check non-error information not on stderr")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_repos()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
