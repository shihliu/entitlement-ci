from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537216_yum_repolist_right_after_attach_multi_attribute_subscriptions_without_error(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_ram")
                password = self.get_rhsm_cons("password_ram")
                self.sub_register(username, password)
                facts_value = "echo \'{\"virt.is_guest\": \"True\"}' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update"
                self.set_facts(facts_value)
                # change facts
                facts_value = "echo \'{\"cpu.core(s)_per_socket\":\"4\",\"cpu.cpu_socket(s)\":\"2\",\"memory.memtotal\":\"30000000\"}' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update" 
                self.set_facts(facts_value)
                # auto-attach
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)
                # yum repolist
                cmd = "yum repolist"
                (ret, output) = self.runcmd(cmd, "yum repolist")
                if ret == 0:
                    logger.info("It's successful to yum repolist")
                else:
                    raise FailException("Test Failed - Failed to yum repolist")

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
