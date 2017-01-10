from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537280_when_partially_subscribed_autosubscribe_could_choose_a_more_efficient_pool_to_consume(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_socket")
                password = self.get_rhsm_cons("password_socket")
                self.sub_register(username, password)

                # auto-attach
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)
                out1 = self.list_consumed()

                # change facts to make partial subscribed
                facts_value = "echo \'{\"virt.is_guest\": \"False\",\"cpu.cpu_socket(s)\":\"4\"}' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update" 
                self.set_facts(facts_value) 
                out_partial = self.list_consumed()
                if 'Status Details:      Only supports' in out_partial:
                    logger.info("It's successful to check partial subscribed")
                else:
                    raise FailException("Test Failed - Failed to check partial subscribed")

                # auto-attach again
                self.sub_autosubscribe(autosubprod)
                out2 = self.list_consumed()
                
                if out1 == out2:
                    logger.info("It's successful to verify a_more_efficient_pool_to_consume")
                else:
                    raise FailException("Test Failed - Failed to verify a_more_efficient_pool_to_consume")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.remove_facts_value()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_consumed(self):
        cmd = "subscription-manager list --consumed"
        (ret, output) = self.runcmd(cmd, "list consumed")
        if ret == 0:
            logger.info("It's successful to list consumed")
            return output
        else:
            raise FailException("Test Failed - Failed to list consumed")

if __name__ == "__main__":
    unittest.main()
