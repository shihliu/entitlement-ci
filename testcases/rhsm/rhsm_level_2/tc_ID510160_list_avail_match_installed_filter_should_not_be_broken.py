from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510160_list_avail_match_installed_filter_should_not_be_broken(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # check if only one product installed
            cmd = "subscription-manager list --installed | grep 'Product ID:' | wc -l"
            (ret, output) = self.runcmd(cmd, "check if only one product installed")
            if ret ==0 and '1' == output.strip():
                logger.info("It's successful to check only one product installed")
            else:
                raise FailException("Test Failed - Failed to check only one product installed")

            # list all available subscriptions
            cmd = "subscription-manager list --avail --all | grep SKU | wc -l"
            (ret, output) = self.runcmd(cmd, "list all available subscriptions")
            if ret ==0:
                logger.info("It's successful to list all available subscriptions")
                all_avail = output.strip()
            else:
                raise FailException("Test Failed - Failed to list all available subscriptions")

            # list matching installed subscription
            cmd = " subscription-manager list --avail --match-installed | grep SKU | wc -l"
            (ret, output) = self.runcmd(cmd, "list matching installed subscription")
            if ret ==0:
                logger.info("It's successful to list matching installed subscription")
                matching_avail = output.strip()
            else:
                raise FailException("Test Failed - Failed to list matching installed subscription")

            # check if  list --avail --match-installed filter is broken
            if int(all_avail) > int(matching_avail):
                logger.info("It's successful to check list --avail --match-installed filter is not broken")
            else:
                raise FailException("Test Failed - Failed to check list --avail --match-installed filter is not broken")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_repos()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
