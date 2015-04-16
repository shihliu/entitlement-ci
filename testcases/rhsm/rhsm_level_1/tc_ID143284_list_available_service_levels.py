from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID143284_list_available_service_levels(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        # register to server
        username = RHSMConstants().get_constant("username")
        password = RHSMConstants().get_constant("password")
        self.sub_register(username, password)

        try:
            # list available service levels
            service_level = RHSMConstants().get_constant("servicelevel")
            cmd = "subscription-manager service-level --list"
            (ret, output) = self.runcmd(cmd, "list available service levels")
            if (ret == 0) and ("service_level" in output or "Service Levels" in output):
                logger.info("It's successful to list available service levels.")
            else:
                raise FailException("Test Failed - Failed to list available service levels.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
