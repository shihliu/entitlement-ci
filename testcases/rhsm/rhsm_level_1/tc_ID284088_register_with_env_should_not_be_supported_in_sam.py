from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID284088_register_with_env_should_not_be_supported_in_sam(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            org = self.get_rhsm_cons("default_org")
            # Register with env option
            cmd = "subscription-manager register --username=%s --password=%s --org=%s --env=Library" % (username, password, org)
            (ret, output) = self.runcmd(cmd, "register with environments")
            if (self.test_server == "SAM" or self.test_server == "STAGE") and ret != 0 and "Error: Server does not support environments." in output:
                logger.info("It's successful to verify that register_with_env_should_not_be_supported_in_sam")
            elif self.test_server == "SATELLITE" and ret == 0 and "The system has been registered with ID" in output:
                logger.info("It's successful to verify that registration with envionments is supported in satellite")
            else:
                raise FailException("Test Failed - failed to verify registration with envionments")
            # Check env help info
            cmd = "subscription-manager environments --help"
            (ret, output) = self.runcmd(cmd, "check environments help")
            if ret == 0 and "Display the environments available for a user" in output:
                logger.info("It's successful to check environment help info")
            else:
                raise FailException("Test Failed - failed to check environment help info")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
