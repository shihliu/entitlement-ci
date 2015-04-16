from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115198_listavailrepos(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        # register to server
        username = RHSMConstants().get_constant("username")
        password = RHSMConstants().get_constant("password")
        self.sub_register(username, password)

        autosubprod = RHSMConstants().get_constant("autosubprod")
        self.sub_autosubscribe(autosubprod)

        productrepo = RHSMConstants().get_constant("productrepo")
        betarepo = RHSMConstants().get_constant("betarepo")
        try:
            cmd = "subscription-manager repos --list"
            (ret, output) = self.runcmd(cmd, "list available repos")
            if ret == 0 and productrepo in output and betarepo in output:
                logger.info("It's successful to list available repos.")
            else:
                raise FailException("Test Failed - Failed to list available repos.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
