from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537267_appropriate_message_when_query_service_level_to_another_server(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # query service level on another server
            cmd = "subscription-manager service-level --serverurl subscription.rhn.redhat.com:443/subscription"
            (ret, output) = self.runcmd(cmd, "set server hostname")
            if ret != 0 and 'Invalid credentials' in output:
                logger.info("It's successful to verify that proper info displayed when query service level to another server")
            else:
                raise FailException("Test Failed - Failed to verify that proper info displayed when query service level to another server")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
