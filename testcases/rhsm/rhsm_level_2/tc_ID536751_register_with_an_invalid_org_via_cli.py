from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536751_register_with_an_invalid_org_via_cli(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            #Register with invalid org
            invalid_org = '--org=invalidorg'
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            cmd = 'subscription-manager register --username=%s --password=%s %s'%(username, password, invalid_org)
            (ret, output) = self.runcmd(cmd, "register with invalid org")
            if ret != 0 and ("Couldn\'t find organization" in output or "Organization invalidorg does not exist." in output or "Couldn\'t find Organization \'invalidorg\'" in output):
                logger.info("It's successful to check registration with invalid org")
            else:
                raise FailException("Test Failed - Failed to check registration with invalid org")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
