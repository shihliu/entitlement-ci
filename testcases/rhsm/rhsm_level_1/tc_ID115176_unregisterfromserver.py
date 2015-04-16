from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115176_unregisterfromserver(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # unregister from server
            cmd = "subscription-manager unregister"
            (ret, output) = self.runcmd(cmd, "unregister")
            if ret == 0:
                if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                    logging.info("It's successful to unregister.")
                else:
                    raise FailException("Test Failed - The information shown after unregistered is not correct.")
            else:
                raise FailException("Test Failed - Failed to unregister.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
