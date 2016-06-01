from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID190673_unsubscribe_with_no_options(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            cmd = "subscription-manager unsubscribe"
            (ret, output) = self.runcmd(cmd, "running unsubscribe command with no options")
            if ret != 0 and ("Error: This command requires that you specify one of --serial or --all" in output or "Error: This command requires that you specify one of --serial, --pool or --all." in output):
                logger.info("It's successful to check the error message when run unsubscribe with no options.")
            else:
                raise FailException("Test Failed - Failed to check the error message when run unsubscribe with no options.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
