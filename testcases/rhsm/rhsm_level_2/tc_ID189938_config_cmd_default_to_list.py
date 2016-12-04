from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID189938_config_cmd_default_to_list(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # run cmd with config only
            cmd = "subscription-manager config"
            (ret, output) = self.runcmd(cmd, "running config without option")
            configout = output
            # run cmd with config --list
            cmd = "subscription-manager config --list"
            (ret, output) = self.runcmd(cmd, "running config with option --list")
            configlistout = output
            if configout == configlistout:
                logger.info("It's successful to verify config cmd with list option by default - the output of both config and config --list is the same.")
            else:
                raise FailException("Test Failed - Failed to verify config cmd with list option by default - the output of both config and config --list is not the same.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()