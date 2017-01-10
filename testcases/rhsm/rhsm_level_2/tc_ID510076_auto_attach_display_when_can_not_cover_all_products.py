from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510076_auto_attach_display_when_can_not_cover_all_products(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # get a new product cert
            self.add_new_product_cert()

            # auto-attach
            cmd = 'subscription-manager attach --auto'
            (ret, output) = self.runcmd(cmd, "auto-attach")
            if 'Unable to find available subscriptions for all your installed products.' in output:
                logger.info("It's successful to display auto-attach when can not cover all products")
            else:
                raise FailException("Test Failed - Failed to display auto-attach when can not cover all products")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # remove new product cert
            self.rm_new_product_cert()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
