from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509585_autoattach_with_single_SLA(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            servicelevel = self.get_rhsm_cons("servicelevel")
            cmd = "subscription-manager attach --auto --servicelevel=%s"%servicelevel
            (ret, output) = self.runcmd(cmd, "auto-attach with servicelevel")
            if ret == 0 and 'Service level set to: %s'%servicelevel in output:
                logger.info("It's successful to auto-attach with servicelevel")
            else:
                raise FailException("Test Failed - Failed to register with activationkey")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
