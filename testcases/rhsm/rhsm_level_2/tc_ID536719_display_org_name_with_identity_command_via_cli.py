from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536719_display_org_name_with_identity_command_via_cli(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            orgid = self.get_rhsm_cons("default_org")

            # check org info by identity command
            cmd = "subscription-manager identity | grep -E 'org name|org ID'"
            (ret, output) = self.runcmd(cmd, "check org info")

            if ret == 0 and orgid in output:
                logger.info("It's successful to check org info by identity")
            else:
                raise FailException("Test Failed - Failed to check org info by identity")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
