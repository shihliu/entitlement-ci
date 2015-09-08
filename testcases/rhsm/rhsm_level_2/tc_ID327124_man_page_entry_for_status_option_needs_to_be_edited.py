from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID327124_man_page_entry_for_status_option_needs_to_be_edited(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'man subscription-manager | grep "subscription-manager status" -A5'
            (ret, output) = self.runcmd(cmd, "man page entry for status option")
            if ret == 0 and "Overall Status: Current" in output:
                logger.info("It's successful to check man page entry for status option.") 
            else:
                raise FailException("Test Failed - Failed to check man page entry for status option.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
