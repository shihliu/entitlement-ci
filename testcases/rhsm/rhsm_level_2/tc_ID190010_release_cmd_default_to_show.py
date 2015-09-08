from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190010_release_cmd_default_to_show(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # run cmd with release only
            cmd = "subscription-manager release"
            (ret, output) = self.runcmd(cmd, "running release without option")
            releaseout = output
            # run cmd with release --show
            cmd = "subscription-manager release --show"
            (ret, output) = self.runcmd(cmd, "running release with option: --show")
            releaseshowout = output
            if releaseout == releaseshowout :
                logger.info("It's successfull to check the default output of release: the output of release is the same as release --show!")
            else:
                raise FailException("Test Faild - Failed to check the default output of repos: the output of release is not the same as release --show!")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
