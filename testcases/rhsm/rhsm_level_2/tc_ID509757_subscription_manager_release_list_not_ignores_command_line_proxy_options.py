from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509757_subscription_manager_release_list_not_ignores_command_line_proxy_options(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            cmd = "subscription-manager release --list --proxy=http://squid.corp.redhat.com:3128"
            (ret, output) = self.runcmd(cmd, "list release by proxy option in cli")
            if ret != 0 and 'Network error, unable to connect to server. Please see /var/log/rhsm/rhsm.log for more information.' in output:
                logger.info("It's successful to verify that listing release by proxy")
            else:
                raise FailException("Test Failed - Failed to verify that listing release by proxy")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
