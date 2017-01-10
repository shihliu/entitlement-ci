from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537045_auto_subscribe_for_ram_based_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
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
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # Get the entitlement certs
                cmd = "ls /etc/pki/entitlement | grep -v key"
                (ret, output) = self.runcmd(cmd, "get ent cert")
                ent_cert = output.strip()
                if ret == 0:
                    logger.info("It's successful to get ent cert")
                else:
                    raise FailException("Test Failed - Failed to get ent cert")

                # check ram info in entitlement certs
                cmd = "rct cat-cert /etc/pki/entitlement/%s |grep RAM"%ent_cert
                (ret, output) = self.runcmd(cmd, "check ram info")
                ram_info = output.strip().split(":")[1]
                if ret == 0 and ram_info in output:
                    logger.info("It's successful to check ram info in ent cert")
                else:
                    raise FailException("Test Failed - Failed to check ram info in ent cert")

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
