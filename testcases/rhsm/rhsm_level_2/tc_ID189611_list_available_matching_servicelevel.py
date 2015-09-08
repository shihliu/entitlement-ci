from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID189611_list_available_matching_servicelevel(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # get service_level
            service_level = RHSMConstants().get_constant("servicelevel")
            # list available subscriptions matching specified service level
            cmd = "subscription-manager list --available --servicelevel=%s" % service_level
            (ret, output) = self.runcmd(cmd, "list available subscriptions matching specified service level")
            if ret == 0:
                logger.info("It's successful to list available subscriptions matching specified service level.")
                if self.check_servicelevel_in_listavailable_ouput(output, service_level):
                    logger.info("It's successful to check specified service level in the ouput of listing available subscriptions.")   
                else:
                    raise FailException("Test Failed - Failed to check specified service level in the ouput of listing available subscriptions.")
            else:
                raise FailException("Test Failed - Failed to list available subscriptions matching specified service level.")
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_servicelevel_in_listavailable_ouput(self, output, service_level):
        if "No available subscription pools to list" not in output:
            pool_list = self.parse_listavailable_output(output)
            print "pool_list:\n", pool_list,"\n0000000000"
            for item in pool_list:
                if (item['ServiceLevel']).lower() != (service_level).lower():
                     return False
                else:
                    continue
            return True
        else:
            logger.info("There is no available subscription pools to list!")
            return False

if __name__ == "__main__":
    unittest.main()