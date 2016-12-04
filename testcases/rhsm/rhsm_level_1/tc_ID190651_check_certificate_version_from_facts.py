from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID190651_check_certificate_version_from_facts(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # check the certificate version from facts
            cmd = "subscription-manager facts | grep system.certificate_version"
            (ret, output) = self.runcmd(cmd, "check the certificate version from facts")
            if ret == 0 and "system.certificate_version: 3" in output:
                logger.info("It's successful to check the certificate version from facts.")    
            else:
                raise FailException("Test Failed - Failed to check the certificate version from facts.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
