from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510093_attaching_an_already_expired_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            
            # set client system time to make expiration
            self.set_system_time('20200101')

            # Can not attach against stage when expiration
            if self.test_server == 'STAGE':
                cmd = 'subscription-manager attach'
                (ret, output) = self.runcmd(cmd, "check consumed")
                if ret !=0 and 'Your identity certificate has expired' in output:
                    logger.info("It's successful to check the expired subscription can not be attached against stage")
                else:
                    raise FailException("Test Failed - Failed to check the expired subscription can not be attached against stage")
            else:
                # auto attach
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # check consumed subscription
                cmd = 'subscription-manager list --consumed'
                (ret, output) = self.runcmd(cmd, "check consumed")
                if ret ==0 and 'Active:              False' in output:
                    logger.info("It's successful to check consumed")
                else:
                    raise FailException("Test Failed - Failed to check consumed")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_system_time()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
