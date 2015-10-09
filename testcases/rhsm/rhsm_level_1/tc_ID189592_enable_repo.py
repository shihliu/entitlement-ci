from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID189592_enable_repo(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            if not self.skip_satellite():
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)
                productrepo = self.get_rhsm_cons("productrepo")
                cmd = "subscription-manager repos --list | grep %s" % productrepo
                (ret, output) = self.runcmd(cmd, "check the repo %s" % productrepo)
                if ret == 0 and productrepo in output:
                    logger.info("It's successful to check the repo %s which is available." % productrepo)
                    # enable the repo in list
                    cmd = "subscription-manager repos --enable=%s" % productrepo
                    (ret, output) = self.runcmd(cmd, "enable the repo %s" % productrepo)
                    if ret == 0 and "Repository '%s' is enabled for this system." % productrepo in output:
                        logger.info("It's successful to disable the repo %s." % productrepo)
                    else: 
                        raise FailException("Test Failed - Failed to enable the repo %s." % productrepo)
                else:
                    raise FailException("Test Failed - Fail to check the repo %s which should be available." % productrepo)
                self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
