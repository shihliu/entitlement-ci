from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510136_informing_user_when_adding_an_override_for_non_existing_repo(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            self.remove_all_override()

            # Add an override for a non-existing Repo
            cmd = 'subscription-manager repo-override --repo=tesssssssssss --add=test1:123'
            (ret, output) = self.runcmd(cmd, "Add an override for a non-existing Repo")
            if ret ==0 and "Repository 'tesssssssssss' does not currently exist, but the override has been added" in output:
                logger.info("It's successful to Add an override for a non-existing Repo")
            else:
                raise FailException("Test Failed - Failed to Add an override for a non-existing Repo")

            cmd = 'subscription-manager repo-override --list'
            (ret, output) = self.runcmd(cmd, "list repo-override")
            if ret ==0 and "Repository: tesssssssssss" in output and "test1: 123" in output:
                logger.info("It's successful to list repo-override")
            else:
                raise FailException("Test Failed - Failed to list repo-override")

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
