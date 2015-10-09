from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID189936_facts_cmd_default_to_list(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # run cmd with facts only
            cmd = "subscription-manager facts"
            (ret, output) = self.runcmd(cmd, "running facts without option")
            factsout = output
            # run cmd with facts --list
            cmd = "subscription-manager facts --list"
            (ret, output) = self.runcmd(cmd, "running facts with option: --list")
            factslistout = output
            if factsout == factslistout:
                logger.info("It's successfull to check the default output of repos: the output of facts is the same as facts --list!")
            else:
                raise FailException("Test Faild - It's failed to check the default output of repos: the output of facts is not the same as facts --list!")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
