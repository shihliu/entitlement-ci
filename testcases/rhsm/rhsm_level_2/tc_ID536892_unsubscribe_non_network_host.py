from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536892_unsubscribe_non_network_host(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register and auto-attach
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # cut off connection from server
            active_hostname = self.off_server_connection()

            # unregister
            cmd = "subscription-manager remove --all"
            (ret, output) = self.runcmd(cmd, "register to unconnected server")
            if ret != 0 and 'Network error, unable to connect to server' in output:
                logger.info("It's successful to verify that unsubscribe to unconnected server should fail")
            else:
                raise FailException("Test Failed - Failed to verify that unsubscribe to unconnected server should fail")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_server_hostname(active_hostname)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
