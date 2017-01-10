from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510110_no_subscription_field_in_rct_cat_cert_order(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Check no subscription field in order
            certname = self.get_subscription_serialnumlist()[0]
            cmd = 'rct cat-cert /etc/pki/entitlement/%s.pem | grep Order -A20'%certname
            (ret, output) = self.runcmd(cmd, "check no subscription field in order")
            if ret ==0 and 'Subscription:' not in output:
                logger.info("It's successful to check no subscription field in order")
            else:
                raise FailException("Test Failed - Failed to check no subscription field in order")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
