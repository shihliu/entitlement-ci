from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509852_rct_manifest_modules_should_work_fine_without_error(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Get manifest
            self.get_manifest()

            # Check rct cat-manifest
            cmd = "cd /root;rct cat-manifest sam_install_manifest.zip | grep 'Subscription:' -A1"
            (ret, output) = self.runcmd(cmd, "check rct cat-manifest")
            if ret ==0 and 'Name:' in output:
                logger.info("It's successful to check rct cat-manifest.")
            else:
                raise FailException("Test Failed - Failed to check rct cat-manifest.")

            # Check rct dump-manifest
            cmd = "cd /root;rct dump-manifest -f sam_install_manifest.zip"
            (ret, output) = self.runcmd(cmd, "check rct dump-manifest")
            if ret ==0 and 'The manifest has been dumped to the current directory' in output:
                logger.info("It's successful to check rct dump-manifest.")
            else:
                raise FailException("Test Failed - Failed to check rct dump-manifest.")

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
