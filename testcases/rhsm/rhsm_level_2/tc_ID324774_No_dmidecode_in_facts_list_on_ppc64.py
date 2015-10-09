from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID324774_No_dmidecode_in_facts_list_on_ppc64(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = "subscription-manager facts --list | grep dmidecode"
            (ret, output) = self.runcmd(cmd, "check No dmidecode in facts list on ppc64")
            if ret != 0 and 'python-simplejson' not in output:
                logger.info("It's successful to check No dmidecode in facts list on ppc64")
            else:
                raise FailException("Test Failed - Failed to check No dmidecode in facts list on ppc64.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
