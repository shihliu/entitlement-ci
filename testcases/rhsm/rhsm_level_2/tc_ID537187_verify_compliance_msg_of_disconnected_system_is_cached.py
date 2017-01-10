from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537187_verify_compliance_msg_of_disconnected_system_is_cached(RHSMBase):
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

            # before cutting off server connection, list the installed, consumed, compliant status
            consumed1 = self.check_consumed()
            installed1 = self.check_installed()
            status1 = self.check_compliant_status()

            # cut off connection from server
            active_hostname = self.off_server_connection()

            # after cutting off server connection, list the installed, consumed, compliant status
            consumed2 = self.check_consumed()
            installed2 = self.check_installed()
            status2 = self.check_compliant_status()

            if consumed1 == consumed2 and installed1 == installed2 and status1 == status2:
                logger.info("It's successful to verify that compliance msg of disconnected system is cached")
            else:
                raise FailException("Test Failed - Failed to verify that compliance msg of disconnected system is cached")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_server_hostname(active_hostname)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_consumed(self):
        cmd = "subscription-manager list --consumed"
        (ret, output) = self.runcmd(cmd, "list --consumed")
        if ret == 0:
            return output.strip()
            logger.info("It's successful to list --consumed")
        else:
            raise FailException("Test Failed - Failed to list --consumed")

    def check_installed(self):
        cmd = "subscription-manager list --installed"
        (ret, output) = self.runcmd(cmd, "list --installed")
        if ret == 0:
            return output.strip()
            logger.info("It's successful to list --installed")
        else:
            raise FailException("Test Failed - Failed to list --installed")

    def check_compliant_status(self):
        cmd = "subscription-manager status"
        (ret, output) = self.runcmd(cmd, "check status")
        if ret == 0:
            return output.strip()
            logger.info("It's successful to check status")
        else:
            raise FailException("Test Failed - Failed to check status")

if __name__ == "__main__":
    unittest.main()
