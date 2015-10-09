from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID154592_set_release_version(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        # register to server
        username = self.get_rhsm_cons("username")
        password = self.get_rhsm_cons("password")
        self.sub_register(username, password)
        try:
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # set releases
            currentversion = self.sub_getcurrentversion()
            cmd = "subscription-manager release --set=%s" % (currentversion)
            (ret, output) = self.runcmd(cmd, "set release version")
            if ret == 0 and "Release set to: %s" % (currentversion) in output:
                logger.info("It's successful to set release version.")	
            else:
                raise FailException("Test Failed - Failed to set release version.")
            # check the version in repo list
            cmd = "subscription-manager repos --list|grep 'Repo Url'|grep %s" % currentversion
            cmd510 = "subscription-manager repos --list|grep 'Repo URL'|grep %s" % currentversion
            (ret, output) = self.runcmd(cmd, "list available repos")
            if ret == 0:
                logger.info("It's successful to display the set release version.")
            else:
                (ret, output) = self.runcmd(cmd510, "list available repos")
                if ret == 0:
                    logger.info("It's successful to display the set release version.")
                else:
                    raise FailException("Test Failed - Failed to display the set release version.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
