from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537165_healing_of_multi_attribute_subscription(RHSMBase):
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
                # set autoheal interval
                intervals = '1'
                self.auto_heal_set_interval(intervals)

                # restart rhsmcertd service and wait 2 mins
                self.restart_rhsmcertd()
                time.sleep(120)
                # check consumed status
                cmd = "subscription-manager list --consumed| grep 'Status Details:'"
                (ret, output) = self.runcmd(cmd, "check number")
                if ret == 0 and output.strip().split(':')[1].strip() == 'Subscription is current':
                    logger.info("It's successful to check autoheal")
                else:
                    raise FailException("Test Failed - Failed to check auto heal")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.auto_heal_set_interval('1440')
                self.remove_facts_value()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
