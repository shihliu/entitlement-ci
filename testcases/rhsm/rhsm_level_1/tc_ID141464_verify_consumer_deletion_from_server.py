from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID141464_verify_consumer_deletion_from_server(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register to server
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            system_uuid = self.cm_get_consumerid()
            if self.test_server == "STAGE":
                system_uuid = self.get_hostname()
            # Delete the consumer from server
            server_ip = get_exported_param("SERVER_IP")
            self.server_remove_system(system_uuid, server_ip, self.get_rhsm_cons("username"), self.get_rhsm_cons("password"))

            # Check deleted consumer status
            cmd = "subscription-manager identity"
            (ret, output) = self.runcmd(cmd, "check deleted consumer status")
            if ret != 0:
                logger.info("It's successful to check deleted consumer status.")
            else:
                raise FailException("Test Failed - Failed to check deleted consumer status.")
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
