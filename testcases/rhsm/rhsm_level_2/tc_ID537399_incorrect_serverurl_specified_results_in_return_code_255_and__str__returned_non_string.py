from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537399_incorrect_serverurl_specified_results_in_return_code_255_and__str__returned_non_string(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Specify incorrect "--serverurl" to register the system.
            cmd = "subscription-manager register --serverurl=https://<sat6_fqdn>/ --insecure"
            (ret, output) = self.runcmd(cmd, "check registration with specified wrong serverurl")
            if ret != 0 and output.strip() == 'bash: sat6_fqdn: No such file or directory':
                logger.info("It's successful to check registration with specified wrong serverurl")
            else:
                raise FailException("Test Failed - Failed to check registration with specified wrong serverurl")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
