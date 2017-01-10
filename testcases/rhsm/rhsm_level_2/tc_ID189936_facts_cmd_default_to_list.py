from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID189936_facts_cmd_default_to_list(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # run cmd with facts only
            cmd = "subscription-manager facts > /root/f1"
            (ret, output) = self.runcmd(cmd, "running facts without option")
            if ret == 0:
                logger.info("It's successfull to list facts without --list!")
            else:
                raise FailException("Test Faild - Failed to list facts without --list!")

            # run cmd with facts --list
            cmd = "subscription-manager facts --list > /root/f2"
            (ret, output) = self.runcmd(cmd, "running facts with option: --list")
            if ret == 0:
                logger.info("It's successfull to list facts with --list!")
            else:
                raise FailException("Test Faild - Failed to list facts with --list!")

            cmd = "cd /root/; diff f1 f2 -I ^'lscpu.cpu_mhz:'"
            (ret, output) = self.runcmd(cmd, "compare the facts")
            if ret == 0 and output.strip() == '':
                logger.info("It's successfull to check the default output of repos: the output of facts is the same as facts --list!")
            elif ret != 0 and output.strip() == '3' and 'lscpu.cpu_mhz: ' in output:
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
