from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537170_partial_subscription_of_multi_attribute_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_ram")
                password = self.get_rhsm_cons("password_ram")
                self.sub_register(username, password)
                
                # auto-attach
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)
                    
                # change facts
                facts_value = "echo \'{\"cpu.core(s)_per_socket\":\"8\",\"cpu.cpu_socket(s)\":\"2\",\"memory.memtotal\":\"40000000\"}' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update" 
                self.set_facts(facts_value)             

                # list consumed for provides field
                cmd = "subscription-manager status |grep 'Overall Status:'"
                (ret, output) = self.runcmd(cmd, "check number")
                if ret == 0 and output.strip().split(':')[1].strip() == 'Insufficient':
                    logger.info("It's successful to check number blank in consumed")
                else:
                    raise FailException("Test Failed - Failed to check number blank in consumed")

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
