from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537348_update_sub_man_man_page_for_new_list_options(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            info1 = '--no-overlap          shows pools which provide products that are not\n                        already covered; only used with --available'
            info2 = '--match-installed     shows only subscriptions matching products that are\n                        currently installed; only used with --available'
            info3 = '--matches=FILTER_STRING\n                        lists only subscriptions or products containing the\n                        specified expression in the subscription or product\n                        information, varying with the list requested and the\n                        server version (case-insensitive).'
            info4 = '--pool-only           lists only the pool IDs for applicable available or\n                        consumed subscriptions; only used with --available and\n                        --consumed'
            cmd = "subscription-manager list --available --help"
            (ret, output) = self.runcmd(cmd, "check new list options")
            if ret == 0 and info1 in output and info2 in output and info3 in output and info4 in output:
                logger.info("It's successful to check new list options")
            else:
                raise FailException("Test Failed - Failed to check new list options")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
