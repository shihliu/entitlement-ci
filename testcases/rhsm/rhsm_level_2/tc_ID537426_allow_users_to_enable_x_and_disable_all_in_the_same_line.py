from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537426_allow_users_to_enable_x_and_disable_all_in_the_same_line(RHSMBase):
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

                os_serial = self.os_serial
                repo1 = 'rhel-server-rhscl-'+os_serial+'-beta-rpms'
                reposet1 = 'rhel-'+os_serial+'-server*'
                reposet2 = 'rhel-server-rhscl*'

                # Disable specified and then enable all
                cmd = "subscription-manager repos --disable=%s --enable=%s --enable=%s; yum repolist all > /root/repostatus; grep %s /root/repostatus"%(repo1, reposet1, reposet2, repo1)
                (ret, output) = self.runcmd(cmd, "disable specified and then enable all")
                if ret == 0 and 'enabled' in output:
                    logger.info("It's successful to check disable specified and then enable all")
                else:
                    raise FailException("Test Failed - Failed to check disable specified and then enable all")

                # Enable all and disable one repo
                cmd = "subscription-manager repos --enable=%s --enable=%s --disable=%s; yum repolist all> /root/repostatus; grep %s /root/repostatus"%(reposet1, reposet2, repo1, repo1)
                (ret, output) = self.runcmd(cmd, "enable all and disable one repo")
                if ret == 0 and 'disabled' in output:
                    logger.info("It's successful to check enable all and disable one repo")
                else:
                    raise FailException("Test Failed - Failed to check enable all and disable one repo")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
