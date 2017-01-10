from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537408_cli_list_available_include_suggested_field(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            #list available subscriptions with date
            cmd="subscription-manager list --available | grep Suggested"
            (ret,output)=self.runcmd(cmd,"list consumed subscriptions")
            if ret == 0 and 'Suggested:' in output:
                logger.info("It's successful to list available subscriptions suggested feild.")
            else:
                raise FailException("Test Failed - Failed to list available subscriptions suggested feild.")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
