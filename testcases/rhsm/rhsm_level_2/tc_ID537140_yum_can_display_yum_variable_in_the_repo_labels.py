from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537140_yum_can_display_yum_variable_in_the_repo_labels(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_satellite_check():
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # Get the vars
                enabled_repo = self.get_rhsm_cons("productrepo")
                cmd = 'grep -A11 "\[%s\]" /etc/yum.repos.d/redhat.repo | grep ui_repoid_vars'%enabled_repo
                (ret, output) = self.runcmd(cmd, "get yum vars")
                if ret == 0 and output.strip() == 'ui_repoid_vars = releasever basearch':
                    logger.info("It's successful to get yum vars")
                else:
                    raise FailException("Test Failed - Failed to get yum vars")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
