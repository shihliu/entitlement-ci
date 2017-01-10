from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537059_facts_update_after_consumer_deleted_from_server(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # Delete the consumer from server
            system_uuid = self.cm_get_consumerid()
            if self.test_server == "STAGE":
                system_uuid = self.get_hostname()
            server_ip = get_exported_param("SERVER_IP")
            self.server_remove_system(system_uuid, server_ip, self.get_rhsm_cons("username"), self.get_rhsm_cons("password"))

            # Update facts
            cmd = 'subscription-manager facts --update'
            (ret, output) = self.runcmd(cmd, "update facts after delete consumer from server side")
            if ret != 0 and ('has been deleted' in output or 'system is not yet registered' in output):
                logger.info("It's successful to check updating facts after delete consumer from server side")
            else:
                raise FailException("Test Failed - Failed to check updating facts after delete consumer from server side")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
