from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID189600_set_wrong_servicelevel(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # set a wrong service level such as notreal
            cmd = "subscription-manager service-level --set=notreal"
            (ret, output) = self.runcmd(cmd, "set a wrong service level")
            if ret != 0 and "Service level 'notreal' is not available to units of organization " in output:      
                logging.info("It's successful to check the error message when set a wrong service level.")
            else:
                raise FailException("Test Failed - Failed to check the error message when set a wrong service level.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()