from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510070_list_available_output_should_include_contract_number(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Check contract number in list-avail
            cmd = 'subscription-manager list --available | grep Contract|head -1'
            (ret, output) = self.runcmd(cmd, "Check contract number in list-available")
            output = output.strip().split(":")[1].strip()
            if ret ==0 and 'None' not in output and 'none' not in output:
                logger.info("It's successful to check contract number in list-available")
            else:
                raise FailException("Test Failed - Failed to check contract number in list-available")
            
            # Check contract number in list-consumed
            cmd = 'subscription-manager list --consumed | grep Contract|head -1'
            (ret, output) = self.runcmd(cmd, "Check contract number in list-consumed")
            output = output.strip().split(":")[1].strip()
            if ret ==0 and 'None' not in output and 'none' not in output:
                logger.info("It's successful to check contract number in list-consumed")
            else:
                raise FailException("Test Failed - Failed to check contract number in list-consumed")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
