from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510055_yum_repolist_when_the_system_date_is_invalid_in_subscriptions_valid_time(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_stage_check():
            try:
                self.check_and_backup_yum_repos()
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # Yum repolist
                cmd = 'yum repolist'
                (ret, output) = self.runcmd(cmd, "yum repolist")
                if ret == 0 and 'Loaded plugins:' in output and 'repolist:' in output:
                    logger.info("It's successful to yum repolist")
                else:
                    raise FailException("Test Failed - Failed to yum repolist")

                # Clean all repo
                cmd = 'yum clean all'
                (ret, output) = self.runcmd(cmd, "yum repolist")
                if (ret == 0 and ('Cleaning up everything' in output or 'Cleaning up Everything' in output) or (ret != 0 and 'There are no enabled repos' in output)):
                    logger.info("It's successful to clean all repo")
                else:
                    raise FailException("Test Failed - Failed to clean all repo")

                # In order to not influence other test, just set client time to expire
                self.set_system_time('20200101')

                # Yum repolist
                cmd = 'yum repolist'
                (ret, output) = self.runcmd(cmd, "check yum repolist 0")
                if ret == 0 and 'repolist: 0' in output:
                    logger.info("It's successful to check yum repolist ")
                else:
                    raise FailException("Test Failed - Failed to check yum repolist 0")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_system_time()
                self.restore_environment()
                self.restore_repos()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
