from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536926_provides_field_remains_blank_when_list_consumed_without_products_provided(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_mgtaddon")
                password = self.get_rhsm_cons("password_mgtaddon")
                self.sub_register(username, password)

                # get available pool
                pools = self.sub_list_availablepool_list()
                cmd = "subscription-manager attach --pool=%s"%pools[0]
                (ret, output) = self.runcmd(cmd, "attach pool")
                if ret == 0:
                    logger.info("It's successful to attach pool")
                else:
                    raise FailException("Test Failed - Failed to attach pool")

                # list consumed for provides field
                cmd = "subscription-manager list --consumed| grep 'Provides:'"
                (ret, output) = self.runcmd(cmd, "check number")
                if ret == 0 and output.strip() == 'Provides:':
                    logger.info("It's successful to check number blank in consumed")
                else:
                    raise FailException("Test Failed - Failed to check number blank in consumed")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
