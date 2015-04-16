from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID189602_clear_current_servicelevel(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register to server
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # get service_level
            service_level = RHSMConstants().get_constant("servicelevel")
            # (1)Test 1: with --set=\"\" option
            # set service-level as precondition
            self.sub_set_servicelevel(service_level)
            # clear current service level by subscription-manager service-level --set=""
            cmd = "subscription-manager service-level --set=\"\""
            (ret, output) = self.runcmd(cmd, "clear current service level with --set=\"\" option")
            if ret == 0 and "Service level preference has been unset" in output:	  
                logger.info("It's successful to clear current service level with --set=\"\" option.")	
            else:
                raise FailException("Test Failed - Failed to clear current service level with --set=\"\" option.")
            # (2)Test 2: with --unset option	
            # set service-level as precondition
            self.sub_set_servicelevel(service_level)
            # clear current service level by subscription-manager service-level --unset
            cmd = "subscription-manager service-level --unset"
            (ret, output) = self.runcmd(cmd, "clear current service level with --unset option")
            if ret == 0 and "Service level preference has been unset" in output:	  
                logging.info("It's successful to clear current service level with --unset option.")	
            else:
                raise FailException("Test Failed - Failed to clear current service level with --unset option.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
