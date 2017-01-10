from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509971_rhsm_man_page_should_indicate_option_org_when_using_activation_key_to_register(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = "man subscription-manager | grep activation"
            (ret, output) = self.runcmd(cmd, "check sm man page for activation key")
            if ret == 0 and 'subscription-manager register --org="IT Dept" --activationkey=' in output:
                logger.info("It's successful to check sm man page for activation key")
            else:
                raise FailException("Test Failed - Failed to check sm man page for activation key")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
