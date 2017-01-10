from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536903_list_available_pools_with_date_to_search(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # get a valid date
            cmd = 'rct cat-cert /etc/pki/consumer/cert.pem  | grep Start'
            (ret,output)=self.runcmd(cmd,"get valid date")
            if ret == 0:
                datetoday = output.split(':')[1].strip().split(' ')[0]
                logger.info("It's successful to get a valid date")
            else:
                raise FailException("Test Failed - Failed to get a valid date")

            #list available subscriptions with date
            cmd="subscription-manager list --available --ondate=%s"%datetoday
            (ret,output)=self.runcmd(cmd,"list consumed subscriptions")
            if ret == 0 and 'Subscription Name:' in output:
                logger.info("It's successful to list available subscriptions with date.")
            else:
                raise FailException("Test Failed - Failed to list available subscriptions with date.")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
