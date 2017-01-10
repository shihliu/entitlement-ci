from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537190_verify_compliance_message_when_subscription_is_compliant(RHSMBase):
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

            # list installed status details
            cmd_installed = 'subscription-manager list --installed | grep Details'
            details_installed = self.list_status_details(cmd_installed)
            if details_installed.split(':')[1].strip() == '':
                logger.info("It's successful to verify compliance msg in installed output is empty")
            else:
                raise FailException("Test Failed - Failed to verify compliance msg in installed output is empty")

            # list consumed status details
            cmd_consumed = 'subscription-manager list --consumed | grep Details'
            details_consumed = self.list_status_details(cmd_consumed)
            if details_consumed.split(':')[1].strip() == 'Subscription is current':
                logger.info("It's successful to verify compliance msg in consumed output is simple")
            else:
                raise FailException("Test Failed - Failed to verify compliance msg in consumed output is simple")

            # list overall status details
            cmd_consumed = 'subscription-manager status | grep Overall'
            details_consumed = self.list_status_details(cmd_consumed)
            if details_consumed.split(':')[1].strip() == 'Current':
                logger.info("It's successful to verify compliance msg in overall output is current")
            else:
                raise FailException("Test Failed - Failed to verify compliance msg in overall output is current")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_status_details(self, cmd):
        (ret, output) = self.runcmd(cmd, "list status details")
        if ret == 0:
            return output
            logger.info("It's successful to list status details")
        else:
            raise FailException("Test Failed - Failed to list status details")


if __name__ == "__main__":
    unittest.main()
