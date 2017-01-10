from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509830_some_repos_like_fastrack_should_be_available_as_they_are_in_rhn(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_satellite_check():
            try:
                self.check_and_backup_yum_repos()
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # Check fastrack repo
                cmd = 'yum repolist all | grep fastrack'
                (ret, output) = self.runcmd(cmd, "check fastrack repo")
                if ret == 0 and '-server-fastrack-rpms' in output and '-server-optional-fastrack-rpms' in output:
                    logger.info("It's successful to check fastrack repo")
                else:
                    raise FailException("Test Failed - Failed to check fastrack repo")

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
