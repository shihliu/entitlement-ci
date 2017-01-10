from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509894_rct_cat_manifest_will_report_contract_from_the_embedded_entitlement_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.get_manifest()

            cmd = 'cd /root;rct cat-manifest sam_install_manifest.zip | grep "Contract:"'
            (ret, output) = self.runcmd(cmd, "check contract info")
            if ret == 0 and 'Contract:' in output:
                logger.info("It's successful to check contract info")
            else:
                raise FailException("Test Failed - Failed to check contract info")

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
