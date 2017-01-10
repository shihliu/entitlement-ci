from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510108_no_traceback_when_yum_repolist_all_or_disabled(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.check_and_backup_yum_repos()
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # no traceback when repolist all
            cmd = 'yum repolist all'
            (ret, output) = self.runcmd(cmd, "check no traceback when repolist all")
            if ret ==0 and 'traceback' not in output and 'Traceback' not in output:
                logger.info("It's successful to check no traceback when repolist all")
            else:
                raise FailException("Test Failed - Failed to check no traceback when repolist all")

            # no traceback when repolist disabled
            cmd = 'yum repolist disabled'
            (ret, output) = self.runcmd(cmd, "check no traceback when repolist disabled")
            if ret ==0 and 'traceback' not in output and 'Traceback' not in output:
                logger.info("It's successful to check no traceback when repolist disabled")
            else:
                raise FailException("Test Failed - Failed to check no traceback when repolist disabled")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            self.restore_repos()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
