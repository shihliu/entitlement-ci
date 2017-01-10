from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509972_system_certificate_version_should_be_3_2_or_more_with_facts_list(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = "subscription-manager facts --list | grep cert"
            (ret, output) = self.runcmd(cmd, "check system.certificate_version")
            if ret == 0 and 'system.certificate_version: 3.2' in output:
                logger.info("It's successful to check system.certificate_version should be 3.2 or more")
            else:
                raise FailException("Test Failed - Failed to check system.certificate_version should be 3.2 or more")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
