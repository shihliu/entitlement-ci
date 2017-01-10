from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536929_repos_command_default_to_list_if_no_options_provided(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_satellite_check():
            try:
                # Register
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # Check repos command
                cmd = "subscription-manager repos > /root/repolist1"
                (ret, output) = self.runcmd(cmd, "repos command")
                if ret == 0:
                    logger.info("It's successful to check repos command")
                else:
                    raise FailException("Test Failed - Failed to check repos command")

                # Check repos --list command
                cmd = "subscription-manager repos --list > /root/repolist2"
                (ret, output) = self.runcmd(cmd, "repos list command")
                if ret == 0:
                    logger.info("It's successful to check repos list command")
                else:
                    raise FailException("Test Failed - Failed to check repos list command")

                # Check results
                cmd = "diff /root/repolist1 /root/repolist2"
                (ret, output) = self.runcmd(cmd, "repos list command")
                if ret == 0 and output.strip() == '':
                    logger.info("It's successful to check repos list command default to list")
                else:
                    raise FailException("Test Failed - Failed to check repos list command default to list")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
