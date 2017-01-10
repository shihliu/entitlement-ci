from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537043_partial_subscribe_ram_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username_ram")
                password = self.get_rhsm_cons("password_ram")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # check installed status for fully subscribed
                status1 = self.check_installed_status()
                if status1 == 'Subscribed':
                    logger.info("It's successful to check installed status of full subscribed")
                else:
                    raise FailException("Test Failed - Failed to check installed status of full subscribed")

                # check change ram facts
                cmd = "echo \'{\"virt.is_guest\" : \"False\", \"memory.memtotal\" : \"330000000\"}\' > /etc/rhsm/facts/custom.facts;subscription-manager facts --update"
                (ret, output) = self.runcmd(cmd, "change ram facts")
                if ret == 0 and 'Successfully updated the system facts.' in output:
                    logger.info("It's successful to chage ram facts")
                else:
                    raise FailException("Test Failed - Failed to chage ram facts")

                # check status
                status1 = self.check_installed_status()
                if status1 == 'Partially Subscribed':
                    logger.info("It's successful to check installed status of full subscribed")
                else:
                    raise FailException("Test Failed - Failed to check installed status of full subscribed")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                cmd = 'rm -f /etc/rhsm/facts/custom.facts;subscription-manager facts --update'
                (ret, output) = self.runcmd(cmd, "change ram facts")
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
