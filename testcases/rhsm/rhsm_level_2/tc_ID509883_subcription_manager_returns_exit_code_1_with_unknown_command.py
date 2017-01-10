from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509883_subcription_manager_returns_exit_code_1_with_unknown_command(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
#            username = self.get_rhsm_cons("username")
#            password = self.get_rhsm_cons("password")
#            self.sub_register(username, password)
#            autosubprod = self.get_rhsm_cons("autosubprod")
#            self.sub_autosubscribe(autosubprod)
            cmd = "subscription-manager fool"
            (ret, output) = self.runcmd(cmd, "run unknow command")
            if ret == 1 and ("Usage: subscription-manager MODULE-NAME [MODULE-OPTIONS] [--help]" in output):
                logger.info("subscription-manager output with unknow command is right ")
            else:
                raise FailException("Test Failed - subscription-manager output with unknow command is wrong")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
