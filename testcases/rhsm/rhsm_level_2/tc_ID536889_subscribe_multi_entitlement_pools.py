from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536889_subscribe_multi_entitlement_pools(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_socket")
                password = self.get_rhsm_cons("password_socket")
                self.sub_register(username, password)
                # change facts
                facts_value = "echo \'{\"cpu.cpu_socket(s)\":\"4\"}' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update" 
                self.set_facts(facts_value)             
                # get available pool
                pools = self.sub_list_availablepool_list()
                cmd = "subscription-manager attach --pool=%s --quantity=2"%pools[0]
                (ret, output) = self.runcmd(cmd, "attach pool")
                if ret == 0 and 'Successfully attached a subscription for' in output:
                    logger.info("It's successful to attach pool with quantity")
                else:
                    raise FailException("Test Failed - Failed to attach pool with quantity")

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
