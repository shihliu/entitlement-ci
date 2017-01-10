from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509890_remove_hyphen_from_system_has_been_un_registered(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            cmd = "subscription-manager unregister"
            (ret, output) = self.runcmd(cmd, "check unregister output")
            if ret == 0 and output.strip() == 'System has been unregistered.':
                logger.info("It's successful to check unregister info")
            else:
                raise FailException("Test Failed - Failed to check unregister info")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
