from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID538219_error_when_disable_all_repos_by_sub_man_repos_disable_wildcards(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register and auto-attach
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Disable all repos with * when testing satellite.
            if self.test_server == "SATELLITE":
                output = self.check_repo_disable('*')
                if output == 'Error: \'*\' does not match a valid repository ID. Use "subscription-manager repos --list" to see valid repositories.':
                    logger.info("It's successful to check disabling all repo with * against satellite")
                else:
                    raise FailException("Test Failed - Failed to check disabling all repo with * against satellite")

            # Disable an invalid repo
            output = self.check_repo_disable('qqq')
            if output == 'Error: \'qqq\' does not match a valid repository ID. Use "subscription-manager repos --list" to see valid repositories.':
                logger.info("It's successful to check disabling invalid repo qqq")
            else:
                raise FailException("Test Failed - Failed to check disabling invalid repo qqq")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_repo_disable(self, reponame):
        output = None
        cmd = "subscription-manager repos --disable=%s"%reponame
        (ret, output) = self.runcmd(cmd, "disable repo")
        return output.strip()
        if ret != 0:
            logger.info("It's successful to disable invalid repo")
        else:
            raise FailException("Test Failed - Failed to disable invalid repo")

if __name__ == "__main__":
    unittest.main()
