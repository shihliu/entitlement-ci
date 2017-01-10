from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537383_attaching_sku_rh00073_on_2_socket_physical_system(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_rh00073")
                password = self.get_rhsm_cons("password_rh00073")
                self.sub_register(username, password)

                # change facts
                cmd = "echo '{\"cpu.cpu_socket(s)\":\"2\",\"virt.is_guest\": \"False\"}' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update"
                (ret, output) = self.runcmd(cmd, "change facts")
                if ret == 0:
                    logger.info("It's successful to change facts")
                else:
                    raise FailException("Test Failed - Failed to change facts")

                # list available
                cmd = "subscription-manager list --available | grep -E 'Suggested|Pool'"
                (ret, output) = self.runcmd(cmd, "change facts")
                output = output.strip().split('\n')
                pool_available = output[0].strip().split(":")[1].strip()
                suggest_count = output[1].strip().split(":")[1].strip()
                if ret == 0 and suggest_count == '4':
                    logger.info("It's successful to list available")
                else:
                    raise FailException("Test Failed - Failed to list available")

                # Attaching the first half of the quantity needed to achieve compliance.
                self.attach_half(pool_available)

                # list consumed status
                if 'Only supports 1 of 2 sockets.' in self.list_consumed_status():
                    logger.info("It's successful to verify one of 2 sockets is supported")
                else:
                    raise FailException("Test Failed - Failed to verify one of 2 sockets is supported")

                # Attaching the second half of the quantity needed to achieve compliance.
                self.attach_half(pool_available)

                # list consumed status
                if 'Subscription is current' in self.list_consumed_status():
                    logger.info("It's successful to verify all of sockets is supported")
                else:
                    raise FailException("Test Failed - Failed to verify all of sockets is supported")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.remove_facts_change()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def attach_half(self, pool_available):
        cmd = "subscription-manager attach --pool=%s --quantity=2"%pool_available
        (ret, output) = self.runcmd(cmd, "attach half")
        if ret == 0:
            logger.info("It's successful to attach half")
        else:
            raise FailException("Test Failed - Failed to attach half")

    def list_consumed_status(self):
        cmd = 'subscription-manager list --consumed | grep "Status Details"'
        (ret, output) = self.runcmd(cmd, "list consumed status")
        if ret == 0:
            consu_status = output.strip().split(":")[1].strip()
            return consu_status
            logger.info("It's successful to list consumed status")
        else:
            raise FailException("Test Failed - Failed to list consumed status")

    def remove_facts_change(self):
        cmd = "rm -rf /etc/rhsm/facts/*"
        (ret, output) = self.runcmd(cmd, "remove facts")
        if ret == 0:
            logger.info("It's successful to remove facts")
        else:
            raise FailException("Test Failed - Failed to remove facts")

if __name__ == "__main__":
    unittest.main()
