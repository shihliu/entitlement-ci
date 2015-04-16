from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import re

class tc_ID143283_show_current_service_level(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        # register to server
        username = RHSMConstants().get_constant("username")
        password = RHSMConstants().get_constant("password")
        self.sub_register(username, password)
        try:
            service_level = RHSMConstants().get_constant("servicelevel")
            # auto subscribe with one service level
            cmd = "subscription-manager subscribe --auto --servicelevel=%s" % service_level
            (ret, output) = self.runcmd(cmd, "autosubscribe with one service-level")
            if ret == 0 and (("Status:Subscribed" in output) or re.search("Status:\s+Subscribed", output)):
                cmd = "subscription-manager service-level --show"
                (result, outputnew) = self.runcmd(cmd, "display current service-level")
                if result == 0 and "Current service level: %s" % service_level in outputnew:
                    logger.info("It's successful to display current service level.")
                else:
                    raise FailException("Test Failed - Failed to display current service level.")
            else:
                raise FailException("Test Failed - Failed to auto subscribe with one service level.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
