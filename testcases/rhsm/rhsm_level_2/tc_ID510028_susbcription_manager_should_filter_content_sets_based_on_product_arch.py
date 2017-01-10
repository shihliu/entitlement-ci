from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510028_susbcription_manager_should_filter_content_sets_based_on_product_arch(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # List available numbers
            count_correct_arch = int(self.list_avail_count())

            # Change arch facts and list available numbers
            self.change_arch_facts()
            count_mis_arch = int(self.list_avail_count())

            if count_correct_arch > count_mis_arch:
                logger.info("It's successful to check susbcription-manager filters content sets based on product arch")
            else:
                raise FailException("Test Failed - Failed to check susbcription-manager filters content sets based on product arch")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_facts()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_avail_count(self):
        cmd = 'subscription-manager list --available | grep "Subscription Name:"|wc -l'
        (ret, output) = self.runcmd(cmd, "list available counts")
        if ret ==0:
            return output
            logger.info("It's successful to list available counts")
        else:
            return '0'
            raise FailException("Test Failed - Failed to list available counts")

    def change_arch_facts(self):
        cmd = 'echo \'{"uname.machine":"x390"}\' > /etc/rhsm/facts/custom.facts; subscription-manager facts --update'
        (ret, output) = self.runcmd(cmd, "change arch facts")
        if ret == 0:
            logger.info("It's successful to change arch facts")
        else:
            raise FailException("Test Failed - Failed to change arch facts")

    def restore_facts(self):
        cmd = "rm -f /etc/rhsm/facts/custom.facts; subscription-manager facts --update"
        (ret, output) = self.runcmd(cmd, "restore arch facts")
        if ret == 0:
            logger.info("It's successful to restore arch facts")
        else:
            raise FailException("Test Failed - Failed to restore arch facts")

if __name__ == "__main__":
    unittest.main()
