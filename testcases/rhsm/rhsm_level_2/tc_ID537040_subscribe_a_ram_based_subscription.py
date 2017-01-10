from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537040_subscribe_a_ram_based_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_ram")
                password = self.get_rhsm_cons("password_ram")
                self.sub_register(username, password)
                # disable autoheal
                self.disable_autoheal()
                #remove subscription
                cmd = 'subscription-manager remove --all'
                (ret, output) = self.runcmd(cmd, "rmove subscription ")
                if ret == 0 and 'removed at the server' in output:
                    logger.info("It's successful to remove subscription")
                else:
                    raise FailException("Test Failed - Failed to remove subscription")
                # list available subscription
                cmd = "subscription-manager list --available | grep Pool"
                (ret, output) = self.runcmd(cmd, "get ent cert")
                available_pool = output.strip().split(":")[1].strip()
                if ret == 0:
                    logger.info("It's successful to list avail pool")
                else:
                    raise FailException("Test Failed - Failed to list avail pool")

                # attach the available subscription
                cmd = "subscription-manager attach --pool=%s"%available_pool
                (ret, output) = self.runcmd(cmd, "check ram info")
                if ret == 0 and 'Successfully attached a subscription for' in output:
                    logger.info("It's successful to attach a ram based subscription")
                else:
                    raise FailException("Test Failed - Failed to attach a ram based subscription")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.enable_autoheal()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
