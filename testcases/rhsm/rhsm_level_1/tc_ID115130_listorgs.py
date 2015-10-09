from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID115130_listorgs(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # list orgs of a consumer.
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            cmd = "subscription-manager orgs --username=%s --password=%s" % (username, password)
            (ret, output) = self.runcmd(cmd, "list orgs")
            if ret == 0 and "OrgName" in output and "OrgKey" in output:
                logging.info("It's successful to list orgs info.")
            elif ret == 0 and "Name" in output and "Key" in output:
                logging.info("It's successful to list orgs info.")
            else:
                raise error.TestFail("Test Failed - Failed to list orgs info.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
