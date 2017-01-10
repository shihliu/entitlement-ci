from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509900_description_for_org_needs_clarification_using_org_key(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Check the description of --org for registeration.
            cmd = "subscription-manager register --help | grep ORG -A1"
            (ret, output) = self.runcmd(cmd, "check org for registration")
            if ret == 0 and '--org=ORG_KEY         register with one of multiple organizations for the' in output and 'user, using organization key' in output:
                logger.info("It's successful to check org for registration")
            else:
                raise FailException("Test Failed - Failed to check org for registration")

            # Check the description of --org for listing environments.
            cmd = "subscription-manager environments --help | grep ORG -A1"
            (ret, output) = self.runcmd(cmd, "check org for environments")
            if ret == 0 and '--org=ORG_KEY         specify organization for environment list, using' in output and 'organization key' in output:
                logger.info("It's successful to check org for environments")
            else:
                raise FailException("Test Failed - Failed to check org for environments")

            # Check the description of --org for listing available service levels.
            cmd = "subscription-manager service-level --help | grep ORG -A1"
            (ret, output) = self.runcmd(cmd, "check org for service levels")
            if ret == 0 and '--org=ORG_KEY         specify an organization when listing available service' in output and 'levels using the organization key, only used with' in output:
                logger.info("It's successful to check org for service levels")
            else:
                raise FailException("Test Failed - Failed to check org for service levels")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
