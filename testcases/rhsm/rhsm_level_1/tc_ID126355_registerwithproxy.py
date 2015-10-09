from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID126355_registerwithproxy(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            proxy = self.get_rhsm_cons("proxy_server")
            cmd = "subscription-manager register --username=%s --password=%s --proxy=%s" % (username, password, proxy)
            (ret, output) = self.runcmd(cmd, "register with proxy")
            if ret == 0:
                if ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
                    logger.info("It's successful to register.")
                else:
                    raise FailException("Test Failed - The information shown after registered is not correct.")
            else:
                raise FailException("Test Failed - Failed to register with proxy.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
