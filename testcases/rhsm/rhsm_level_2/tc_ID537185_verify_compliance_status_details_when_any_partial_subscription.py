from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537185_verify_compliance_status_details_when_any_partial_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_arch")
                password = self.get_rhsm_cons("password_arch")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)
                # change facts
                facts_value = "echo \'{\"uname.machine\":\"x390\"}\' > /etc/rhsm/facts/custom.facts > /etc/rhsm/facts/custom.facts;subscription-manager facts --update" 
                self.set_facts(facts_value)             
                # check consumed status
                cmd = "subscription-manager status"
                (ret, output) = self.runcmd(cmd, "check number")
                if ret == 0 and 'Overall Status: Insufficient' in output and 'but the system is x390' in output:
                    logger.info("It's successful to check status")
                else:
                    raise FailException("Test Failed - Failed to check status")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.remove_facts_value()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
