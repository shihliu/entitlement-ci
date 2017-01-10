from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537179_complaince_messaging_for_products_dont_have_subscriptions(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # before register
            status_detail = 'Overall Status: Unknown'
            self.check_status(status_detail)

            status_detail = 'Status:         Unknown\nStatus Details: \n'
            self.check_installed_status(status_detail)

            # Register and auto-attach
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # change facts to make sure no auto-attach
            facts_value = "echo \'{\"uname.machine\":\"x390\"}\' > /etc/rhsm/facts/custom.facts > /etc/rhsm/facts/custom.facts;subscription-manager facts --update" 
            self.set_facts(facts_value)

            status_detail = 'Overall Status: Invalid'
            self.check_status(status_detail)

            status_detail = 'Status:         Not Subscribed\nStatus Details: Not supported by a valid subscription.'
            self.check_installed_status(status_detail)


            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.remove_facts_value()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_status(self, status_detail):
        cmd = "subscription-manager status"
        (ret, output) = self.runcmd(cmd, "check number")
        if ret == 0 and status_detail in output:
            logger.info("It's successful to check status")
        else:
            raise FailException("Test Failed - Failed to check status")

    def check_installed_status(self, status_detail):
        cmd = "subscription-manager list --installed"
        (ret, output) = self.runcmd(cmd, "check number")
        if ret == 0 and status_detail in output:
            logger.info("It's successful to check installed status")
        else:
            raise FailException("Test Failed - Failed to check installed status")

if __name__ == "__main__":
    unittest.main()
