from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID189613_list_consumed_matching_servicelevel(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # get service_level
            service_level = RHSMConstants().get_constant("servicelevel")
            # set service level
            self.sub_set_servicelevel(service_level)
            # auto attach
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # list consumed subscriptions matching specified service level
            cmd = "subscription-manager list --consumed --servicelevel=%s" % service_level
            (ret, output) = self.runcmd(cmd, "list consumed subscriptions matching specified service level")
            if ret == 0 :
                logger.info("It's successful to list consumed subscriptions matching specified service level.")
                if self.check_servicelevel_in_listconsumed_ouput(output, service_level) :
                    logger.info("It's successful to check specified service level in the ouput of listing consumed subscriptions.")
                else:
                    raise FailException("Test Failed - Failed to check specified service level in the ouput of listing consumed subscriptions.")
            else:
                raise FailException("Test Failed - Failed to list consumed subscriptions matching specified service level.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_servicelevel_in_listconsumed_ouput(self, output, service_level):
#        if "No consumed subscription pools to list" not in output:
        if "No consumed subscription pools matching the specified criteria were found" not in output:
            pool_list = self.parse_listavailable_output(output)
            for item in pool_list:
                if item['ServiceLevel'] != service_level:
                    return False
                else:
                    continue
            return True
        else:
            logger.info("There is no consumed subscription pools to list!")
            return False

if __name__ == "__main__":
    unittest.main()