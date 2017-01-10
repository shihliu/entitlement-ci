from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509863_can_register_when_lscpu_on_line_cpu_list_is_not_integer(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # Change facts
            cmd = "echo '{\"lscpu.on-line_cpu(s)_list\" : \"1.8\"}' > /etc/rhsm/facts/custom.facts; subscription-manager facts --update"
            (ret, output) = self.runcmd(cmd, "change facts")
            if ret ==0 and 'Successfully updated the system facts.' in output:
                logger.info("It's successful to change facts")
            else:
                raise FailException("Test Failed - Failed to change facts")

            # Register --force
            cmd = 'subscription-manager register --force --username=%s --password=%s'%(username, password)
            (ret, output) = self.runcmd(cmd, "register --force")
            if ret ==0 and 'has been unregistered' in output and 'The system has been registered with ID' in output:
                logger.info("It's successful to register --force")
            else:
                raise FailException("Test Failed - Failed to register --force")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # restore facts
            self.restore_facts()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def restore_facts(self):
        cmd = 'rm -f /etc/rhsm/facts/custom.facts;subscription-manager facts --update'
        (ret, output) = self.runcmd(cmd, "restore facts")
        if ret ==0 and 'Successfully updated the system facts.' in output:
            logger.info("It's successful to restore facts")
        else:
            raise FailException("Test Failed - Failed to resore facts")

if __name__ == "__main__":
    unittest.main()
