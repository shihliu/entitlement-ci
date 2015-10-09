from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID330287_man_page_entry_for_new_repo_override_module(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Check repo-override module and all of it options in man page
            cmd = "man subscription-manager | col -b | egrep 'REPO-OVERRIDE OPTIONS' -A30"
            (ret, output) = self.runcmd(cmd, "check man page for repo-override")
            if ret == 0 and "REPO-OVERRIDE OPTIONS" in output and "--repo" in output and "--add=NAME:VALUE" in output and "--remove=NAME" in output and "--remove-all" in output and "--list" in output:
                logger.info("It's successful to check man page for repo-override.") 
            else:
                raise FailException("Test Failed - Failed to check man page for repo-override.")
            # Check repo-override option in subscription-manager help
            cmd = "subscription-manager --help | grep repo-override"
            (ret, output) = self.runcmd(cmd, "Check repo-override option in subscription-manager help")
            if ret == 0 and "Manage custom content repository settings" in output:
                logger.info("It's successful to Check repo-override option in subscription-manager help.") 
            else:
                raise FailException("Test Failed - Failed to Check repo-override option in subscription-manager help.")
            # subscription-manager repo-override --help
            cmd = "subscription-manager repo-override --help"
            (ret, output) = self.runcmd(cmd, "Check repo-override help")
            if ret == 0 and "Usage: subscription-manager repo-override [OPTIONS]" in output:
                logger.info("It's successful to Check repo-override help.") 
            else:
                raise FailException("Test Failed - Failed to Check repo-override help.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
