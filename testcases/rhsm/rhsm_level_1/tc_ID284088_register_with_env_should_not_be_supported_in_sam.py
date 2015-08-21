from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID284088_register_with_env_should_not_be_supported_in_sam(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            org = RHSMConstants().get_constant("default_org")
            cmd = "subscription-manager register --username=%s --password=%s --org=%s --env=Library" % (username, password, org)
            (ret, output) = self.runcmd(cmd, "register with environments")
            if ret != 0 and "Error: Server does not support environments." in output:
                logger.info("It's successful to verify that register_with_env_should_not_be_supported_in_sam")
            else:
                raise FailException("Test Failed - failed to verify that register_with_env_should_not_be_supported_in_sam")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
