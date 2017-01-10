from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510139_friendly_informing_while_adding_repo_overrides_exceeding_255_chars(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            self.remove_all_override()

            # Add an override exceeding 255 chars
            cmd = 'subscription-manager repo-override --repo=repo1 --add=param:value_7890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456'
            (ret, output) = self.runcmd(cmd, "check adding an override exceeding 255 chars")
            if ret !=0 and ("Name, value, and label of the override must not exceed 255 characters." in output or "value: size must be between 0 and 255" in output):
                logger.info("It's successful to check adding an override exceeding 255 chars")
            else:
                raise FailException("Test Failed - Failed to check adding an override exceeding 255 chars")

            cmd = 'subscription-manager repo-override --list'
            (ret, output) = self.runcmd(cmd, "list empty repo-override")
            if ret ==0 and "This system does not have any content overrides applied to it." in output:
                logger.info("It's successful to list empty repo-override")
            else:
                raise FailException("Test Failed - Failed to list empty repo-override")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.remove_all_override()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
