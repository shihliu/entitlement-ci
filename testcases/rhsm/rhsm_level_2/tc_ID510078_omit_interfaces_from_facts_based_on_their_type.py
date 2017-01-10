from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510078_omit_interfaces_from_facts_based_on_their_type(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'subscription-manager facts --list | grep "net.interface"'
            (ret, output) = self.runcmd(cmd, "check interface list")
            if ret ==0 and 'net.interface.sit0.mac_address' not in output and 'net.interface.lo.mac_address' not in output:
                logger.info("It's successful to check interface list")
            else:
                raise FailException("Test Failed - Failed to check interface list")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
