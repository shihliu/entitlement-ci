#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509913_subscription_manager_should_check_on_supported_arch_when_calculating_status(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            cmd = "echo '{\"uname.machine\":\"x390\"}' > /etc/rhsm/facts/custom.facts"
            (ret, output) = self.runcmd(cmd, "make a custom.facts file")

            cmd = "subscription-manager facts --update"
            (ret, output) = self.runcmd(cmd, "update the system facts")

            cmd = "subscription-manager status"
            (ret, output) = self.runcmd(cmd, "check the status option's output")
            if ret == 1 and ( "but the system is x390"  in output):
                logger.info("subscription-manager check the arch when calculate the status")
            else:
                raise FailException("Test Failed - subscription-manager doesn't check the arch when calculate the status")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            cmd = "rm -f /etc/rhsm/facts/custom.facts"
            (ret, output) = self.runcmd(cmd, "delete the custom.facts file")
            cmd = "subscription-manager facts --update"
            (ret, output) = self.runcmd(cmd, "update the system facts")
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
