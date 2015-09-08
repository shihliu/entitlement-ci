from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID189618_collapsed_provided_products(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            productid = RHSMConstants().get_constant("productid")
            cmd = "subscription-manager list --consumed"
            (ret, output) = self.runcmd(cmd, "list the consumed products")
            if ret == 0:
                consumed_list = self.parse_listconsumed_output(output)
                if len(consumed_list) == 1 and consumed_list[0]["Provides"] != "":
                    logger.info("It's successful to check collapsed provided products.")
                else:
                    raise FailException("Test Failed - Failed to check collapsed provided products.")
            else:
                raise FailException("Test Failed - Failed to check collapsed provided products.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
