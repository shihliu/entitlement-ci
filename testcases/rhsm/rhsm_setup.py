from utils import *
from testcases.base import Base
from utils.exception.failexception import FailException
from testcases.rhsm.rhsmconstants import RHSMConstants

class rhsm_setup(unittest.TestCase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            Base().configure_testing_server()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
