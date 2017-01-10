from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537236_display_appropriate_message_when_using_unsupported_files_in_rct_cat_manifest_and_dump_manifest(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Check rct cat-manifest
            cmd = "rct cat-manifest /etc/pki/product-default/69.pem"
            (ret, output) = self.runcmd(cmd, "Check rct cat-manifest")
            if ret != 0 and output.strip() == 'Manifest zip is invalid.':
                logger.info("It's successful to check appropriate info when using unsupported files in rct cat-manifest")
            else:
                raise FailException("Test Failed - Failed to check appropriate info when using unsupported files in rct cat-manifest")

            # Check rct cat-manifest
            cmd = "rct dump-manifest /etc/pki/product-default/69.pem"
            (ret, output) = self.runcmd(cmd, "Check rct dump-manifest")
            if ret != 0 and output.strip() == 'Manifest zip is invalid.':
                logger.info("It's successful to check appropriate info when using unsupported files in rct dump-manifest")
            else:
                raise FailException("Test Failed - Failed to check appropriate info when using unsupported files in rct dump-manifest")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
