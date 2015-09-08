from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID189940_repos_cmd_default_to_list(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # run cmd with repos only
            cmd = "subscription-manager repos"
            (ret, output) = self.runcmd(cmd, "running repos without option")
            reposres = self.sub_check_output(output)
            reposout = output.splitlines()
            reposout.sort()
            # run cmd with repos --list
            cmd = "subscription-manager repos --list"
            (ret, output) = self.runcmd(cmd, "running repos with option: --list")
            reposlistres = self.sub_check_output(output)
            reposlistout = output.splitlines()
            reposlistout.sort()
            if reposres and reposlistres and (reposout == reposlistout):
                logger.info("It's successfull to check the default output of repos :the output of repos is the same as repos --list!")
            else:
                raise FailException("Test Faild - Failed to check the default output of repos: the output of repos is not the same as repos --list!")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def sub_check_output(self, output):
        if ("Repo Id:" in output or "Repo ID" in output) and "Repo Name:" in output and ("Repo Url:" in output or "Repo URL" in output) and "Enabled:" in output :
            return True
        else:
            return False

if __name__ == "__main__":
    unittest.main()
