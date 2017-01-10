from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509881_check_auto_option_description_in_subscription_manager_subcribe(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
#            username = self.get_rhsm_cons("username")
#            password = self.get_rhsm_cons("password")
#            self.sub_register(username, password)
#            autosubprod = self.get_rhsm_cons("autosubprod")
#            self.sub_autosubscribe(autosubprod)
            cmd = "subscription-manager subscribe --help | grep auto"
            (ret, output) = self.runcmd(cmd, "run subscribe --help")
            if ret == 0 and ("Automatically attach compatible subscriptions to this" in output):
                logger.info("subscription-manager subscribe --auto's description is right ")
            else:
                raise FailException("Test Failed - subscription-manager subscribe --auto's description is not right")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
