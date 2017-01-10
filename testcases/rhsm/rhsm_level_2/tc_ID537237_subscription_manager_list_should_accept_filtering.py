from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537237_subscription_manager_list_should_accept_filtering(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Check rct cat-manifest
            cmd = "subscription-manager list --help"
            (ret, output) = self.runcmd(cmd, "Check list filtering")
            if ret == 0 and '--matches=FILTER_STRING' in output and '--pool-only' in output:
                logger.info("It's successful to check subscription-manager list accept filtering")
            else:
                raise FailException("Test Failed - Failed to check subscription-manager list accept filtering")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
