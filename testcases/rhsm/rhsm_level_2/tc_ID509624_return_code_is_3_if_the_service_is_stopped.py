from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509624_return_code_is_3_if_the_service_is_stopped(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.stop_rhsmcertd()
            cmd = 'service rhsmcertd status'
            (ret, output) = self.runcmd(cmd, "stop rhsmcertd")
            if ret ==3:
                logger.info("It's successful to verify that return code is 3 when rhsmcertd is stopped.")
            else:
                raise FailException("Test Failed - failed to verify that return code is 3 when rhsmcertd is stopped.")
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restart_rhsmcertd()
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
