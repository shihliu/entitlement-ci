from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510008_negative_proxy_testing_against_subscription_manager_repos_list(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            notes6 = 'Proxy connection failed, please check your settings.'
            notes7_1 = 'Network error, unable to connect to server.'
            notes7_2 = 'Please see /var/log/rhsm/rhsm.log for more information.'
            # with wrong proxy address
            cmd = 'subscription-manager repos --list --proxy=foo'
            (ret, output) = self.runcmd(cmd, "wrong address")
            if ret !=0 and ((notes7_1 in output and notes7_2 in output) or notes6 in output):
                logger.info("It's successful to check repos --list with wrong address")
            else:
                raise FailException("Test Failed - Failed to check repos --list with wrong address")

            # with wrong proxy password
            cmd = 'subscription-manager repos --list --proxy=10.65.193.76:3128 --proxyuser=redhat --proxypassword=bad-password'
            (ret, output) = self.runcmd(cmd, "wrong password")
            if ret !=0 and ((notes7_1 in output and notes7_2 in output) or notes6 in output):
                logger.info("It's successful to check repos --list with wrong password")
            else:
                raise FailException("Test Failed - Failed to check repos --list with wrong password")

            # with wrong proxy port
            cmd = 'subscription-manager repos --list --proxy=10.65.193.76:31290'
            (ret, output) = self.runcmd(cmd, "wrong port")
            if ret !=0 and ((notes7_1 in output and notes7_2 in output) or notes6 in output):
                logger.info("It's successful to check repos --list with wrong port")
            else:
                raise FailException("Test Failed - Failed to check repos --list with wrong port")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
