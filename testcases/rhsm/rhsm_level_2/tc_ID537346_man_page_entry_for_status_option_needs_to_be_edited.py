from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537346_man_page_entry_for_status_option_needs_to_be_edited(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # check status description in man page
            cmd = 'man subscription-manager | grep "subscription-manager status" -A6'
            (ret, output) = self.runcmd(cmd, "check status description")
            if ret == 0 and 'Overall Status: Current' in output and 'Overall Status: Insufficient' in output:
                logger.info("It's successful to check status description in man page")
            else:
                raise FailException("Test Failed - Failed to check status description in man page")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
