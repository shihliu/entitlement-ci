from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510077_service_level_0_is_not_available_to_consumers(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            org = self.get_rhsm_cons("default_org")
            server_type = get_exported_param("SERVER_TYPE")
            cmd = 'subscription-manager register --username=%s --password=%s --org=%s --servicelevel=foo --auto-attach'%(username,password,org)
            (ret, output) = self.runcmd(cmd, "check auto attach with service level {0}")
            if ret !=0 and 'The system has been registered with ID' in output and "Service level 'foo' is not available to units of organization" in output and 'Unable to find available subscriptions for all your installed products' in output:
                logger.info("It's successful to check auto attach with service level {0}")
            else:
                raise FailException("Test Failed - Failed to check auto attach with service level {0}")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
