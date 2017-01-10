from utils import *
from testcases.base import Base
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class RHSM_Stage_Account_Clean(Base):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            rhsm_cons = RHSMConstants()
            username = rhsm_cons.stage_cons["username"]
            password = rhsm_cons.stage_cons["password"]
            self.stage_system_remove_all(username, password)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
