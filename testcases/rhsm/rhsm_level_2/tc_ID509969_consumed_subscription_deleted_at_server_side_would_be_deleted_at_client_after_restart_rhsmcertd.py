from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509969_consumed_subscription_deleted_at_server_side_would_be_deleted_at_client_after_restart_rhsmcertd(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register and auto-attach
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Delete the consumer from server
            system_uuid = self.cm_get_consumerid()
            if self.test_server == "STAGE":
                system_uuid = self.get_hostname()
            server_ip = get_exported_param("SERVER_IP")
            self.server_remove_system(system_uuid, server_ip, self.get_rhsm_cons("username"), self.get_rhsm_cons("password"))

            # Restart rhsmcertd service and sleep 120 mins
            self.restart_rhsmcertd()
            time.sleep(120)
            logger.info("sleep 120 mins ... ")

            # Check deleted consumer status
            if not self.sub_isconsumed(autosubprod):
                logger.info("It's successful to check subscription deleted from client side.")
            else:
                raise FailException("Test Failed - Failed to check subscription deleted from client side.")
            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # clean local consumer and subscription data
            cmd = "subscription-manager clean"
            (ret, output) = self.runcmd(cmd, "clean local data")
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % __name__)

if __name__ == "__main__":
    unittest.main()
