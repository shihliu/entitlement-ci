from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509897_subscription_manager_will_be_changed_to_require_python_dateutils(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # sm needs python-dateutil
            cmd = "rpm -q subscription-manager --requires | grep dateutil"
            (ret, output) = self.runcmd(cmd, "check dependency of python-dateutil")
            if ret == 0 and output.strip() == 'python-dateutil':
                logger.info("It's successful to check dependency of python-dateutil")
            else:
                raise FailException("Test Failed - Failed to check dependency of python-dateutil")

            # sm does not need PyXML
            cmd = "rpm -q subscription-manager --requires | grep PyXML"
            (ret, output) = self.runcmd(cmd, "check independency of PyXML")
            if ret != 0 and output.strip() == '':
                logger.info("It's successful to check independency of PyXML")
            else:
                raise FailException("Test Failed - Failed to check independency of PyXML")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
