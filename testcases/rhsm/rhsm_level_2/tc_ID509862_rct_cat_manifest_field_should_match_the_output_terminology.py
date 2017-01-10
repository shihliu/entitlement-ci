from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509862_rct_cat_manifest_field_should_match_the_output_terminology(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Get manifest
            self.get_manifest()

            # Check fields of rct cat-manifest
            cmd = 'cd /root;rct cat-manifest sam_install_manifest.zip | grep "Subscription" -A20'
            (ret, output) = self.runcmd(cmd, "Check fields of rct cat-manifest")
            if ret ==0 and 'Order:' in output and 'SKU:' in output and 'Service Level:' in output and 'Service Type:' in output:
                logger.info("It's successful to check rct cat-manifest fields")
            else:
                raise FailException("Test Failed - Failed to check rct cat-manifest fields")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.remove_manifest()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
