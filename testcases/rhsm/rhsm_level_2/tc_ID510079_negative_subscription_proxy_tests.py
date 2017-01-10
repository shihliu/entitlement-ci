from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510079_negative_subscription_proxy_tests(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            cmd = 'subscription-manager attach --pool=8a99f9843c01ccba013c04609af80bcc  --proxy=bad-proxy'
            notes6 = 'Proxy connection failed, please check your settings.'
            notes7_1 = 'Network error, unable to connect to server.'
            notes7_2 = 'Please see /var/log/rhsm/rhsm.log for more information.'
            errornotes = "(-2, 'Name or service not known') / (111, 'Connection refused')"
            (ret, output) = self.runcmd(cmd, "check negative proxy test on subscribing")
            if ret !=0 and ((notes7_1 in output and notes7_2 in output) or notes6 in output) and errornotes not in output:
                logger.info("It's successful to check negative proxy test on subscribing")
            else:
                raise FailException("Test Failed - Failed to check negative proxy test on subscribing")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
