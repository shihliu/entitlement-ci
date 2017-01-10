from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537183_complaince_msg_on_socket_products(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_skt4")
                password = self.get_rhsm_cons("password_skt4")
                self.sub_register(username, password)

                # auto-attach
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # change facts to make partial subscribed
                facts_value = "echo \'{\"virt.is_guest\": \"False\",\"cpu.cpu_socket(s)\":\"10\"}' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update" 
                self.set_facts(facts_value) 

                # check list installed status
                msg1 = 'Status:         Partially Subscribed'
                msg2 = 'Status Details: Only supports 4 of 10 sockets.'
                cmd = 'subscription-manager list --installed'
                (ret, output) = self.runcmd(cmd, "list installed status details")
                if ret == 0 and msg1 in output and msg2 in output:
                    logger.info("It's successful to list installed status details")
                else:
                    raise FailException("Test Failed - Failed to list installed status details")

                # check list consumed status
                msg3 = 'Only supports 4 of 10 sockets.'
                cmd = 'subscription-manager list --consumed'
                (ret, output) = self.runcmd(cmd, "list consumed status details")
                if ret == 0 and msg3 in output:
                    logger.info("It's successful to list consumed status details")
                else:
                    raise FailException("Test Failed - Failed to list consumed status details")

                # check overall status
                msg4 = 'Overall Status: Insufficient'
                msg5 = 'Only supports 4 of 10 sockets.'
                cmd = 'subscription-manager status'
                (ret, output) = self.runcmd(cmd, "list consumed status details")
                if ret == 0 and msg4 in output and msg5 in output:
                    logger.info("It's successful to list overall status details")
                else:
                    raise FailException("Test Failed - Failed to list overall status details")

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
