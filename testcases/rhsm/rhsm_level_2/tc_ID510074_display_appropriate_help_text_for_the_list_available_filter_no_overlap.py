from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510074_display_appropriate_help_text_for_the_list_available_filter_no_overlap(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'subscription-manager list --help | grep "no-overlap" -A3'
            (ret, output) = self.runcmd(cmd, "show no-overlap filter help text")
            if ret ==0 and '--no-overlap          shows pools which provide products that are not' in output and 'already covered; only used with --available' in output:
                logger.info("It's successful to show no-overlap filter help text")
            else:
                raise FailException("Test Failed - Failed to show no-overlap filter help text")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
