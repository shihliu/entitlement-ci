from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537044_auto_heal_should_work_with_ram_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_ram")
                password = self.get_rhsm_cons("password_ram")
                self.sub_register(username, password)

                # Change the heal frequency to 1 min
                self.auto_heal_set_interval('1')

                # restart rhsmcertd service
                self.restart_rhsmcertd()

                # sleep 120
                time.sleep(120)

                # check auto heal from list consumed
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_isconsumed(autosubprod)

                # Change the heal frequency to 1440 min
                self.auto_heal_set_interval('1440')

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
