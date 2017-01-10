from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537223_register_or_subscribe_with_wrong_porxy_address_or_wrong_porxyuser_password(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")

            # Register with wrong proxy
            notes6 = 'Proxy connection failed, please check your settings.'
            notes7_1 = 'Network error, unable to connect to server.'
            notes7_2 = 'Please see /var/log/rhsm/rhsm.log for more information.'
            cmd = "subscription-manager register --username=%s --password=%s --proxy=bad-proxy" % (username, password)
            (ret, output) = self.runcmd(cmd, "register with wrong proxy")
            if ret !=0 and ((notes7_1 in output and notes7_2 in output) or notes6 in output):
                logger.info("It's successful to verify friendly error message prompts when registering with wrong proxy")
            else:
                raise FailException("Test Failed - failed to verify friendly error message prompts when registering with wrong proxy")

            # Attach with wrong proxy
            self.sub_register(username, password)
            cmd = "subscription-manager attach --pool=8a99f9843c01ccba013c04609af80bcc --proxy=bad-proxy"
            (ret, output) = self.runcmd(cmd, "Attach with wrong proxy")
            if ret !=0 and ((notes7_1 in output and notes7_2 in output) or notes6 in output):
                logger.info("It's successful to verify friendly error message prompts when attaching with wrong proxy")
            else:
                raise FailException("Test Failed - failed to friendly error message prompts when attaching with wrong proxy")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
