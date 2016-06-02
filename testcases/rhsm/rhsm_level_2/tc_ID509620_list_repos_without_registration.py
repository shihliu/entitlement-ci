from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509620_list_repos_without_registration(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.sub_clean_local_data()
            cmd = 'subscription-manager repos --list'
            (ret, output) = self.runcmd(cmd, "list repos")
            if ret ==0 and 'This system has no repositories available through subscriptions' in output:
                logger.info("It's successful to verify that no available repos for unregistered system")
            else:
                raise FailException("Test Failed - failed to verify registration with envionments")
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
