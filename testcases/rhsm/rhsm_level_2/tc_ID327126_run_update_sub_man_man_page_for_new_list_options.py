from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID327126_run_update_sub_man_man_page_for_new_list_options(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'subscription-manager list --available --help | egrep "no-overlap|match-installed" -A1'
            (ret, output) = self.runcmd(cmd, "check subscription-manager man page for new list options")
            if ret == 0 and "shows pools which provide products that are not" in output and "already covered; only used with --available" in output and "shows only subscriptions matching products that are" in output and "currently installed; only used with --available" in output:
                logger.info("It's successful to check subscription-manager man page for new list options.") 
            else:
                raise FailException("Test Failed - Failed to check subscription-manager man page for new list options.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
