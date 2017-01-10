from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510133_repo_override_should_unwrap_error_list_and_print_to_stderr(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Check error list
            cmd = 'subscription-manager repo-override --repo=awesomeos-ppc --repo=foo --add=baseurl:https://cdn.redhat.com/foo-testing 1>/tmp/stdout 2>/tmp/stderr'
            (ret, output) = self.runcmd(cmd, "check error list")
            if ret !=0:
                cmd1 = 'cat /tmp/stdout'
                cmd2 = 'cat /tmp/stderr'
                (ret1, output1) = self.runcmd(cmd1, "check stdout")
                (ret2, output2) = self.runcmd(cmd2, "check stderr")
                if output1.strip()=='' and 'Not allowed to override values for: baseurl' in output2:
                    logger.info("It's successful to check repo_override_should_unwrap_error_list_and_print_to_stderr")
            else:
                raise FailException("Test Failed - Failed to check repo_override_should_unwrap_error_list_and_print_to_stderr")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
