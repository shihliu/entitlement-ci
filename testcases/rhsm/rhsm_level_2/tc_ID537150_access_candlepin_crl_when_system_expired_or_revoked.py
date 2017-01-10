from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537150_access_candlepin_crl_when_system_expired_or_revoked(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "SAM" :
            try:
                # Register and auto-attach
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)

                # remove subscription
                self.sub_unsubscribe()

                # check pkg installation status
                revoke_info1 = 'This system is registered to Red Hat Subscription Management, but is not receiving updates. You can use subscription-manager to assign subscriptions.'
                revoke_info2 = 'This system is registered with an entitlement server, but is not receiving updates. You can use subscription-manager to assign subscriptions.'
                revoke_status = self.check_installation()
                if revoke_info1 or revoke_info2 in revoke_status:
                    logger.info("It's successful to verify that system should not be able to access CDN bits through thumbslug proxy")
                else:
                    raise FailException("Test Failed - Failed to verify that system should not be able to access CDN bits through thumbslug proxy")

                # auto-attach and make the system expired
                self.sub_autosubscribe(autosubprod)
                self.set_system_time('20200101')

                # check pkg installation status
                expired_info = "You no longer have access to the repositories that provide these products.  It is important that you apply an active subscription in order to resume access to security and other critical updates. If you don't have other active subscriptions, you can renew the expired subscription."
                expired_status = self.check_installation()
                if revoke_info1 or revoke_info2 in expired_status and expired_info in expired_status:
                    logger.info("It's successful to verify that system should not be able to access CDN bits through thumbslug  proxy")
                else:
                    raise FailException("Test Failed - Failed to verify that system should not be able to access CDN bits through thumbslug  proxy")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_system_time()
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_installation(self):
        output = None
        cmd = 'yum install -y zsh'
        (ret, output) = self.runcmd(cmd, "check installation info")
        return output
        if ret != 0:
            logger.info("It's successful to check installation info")
        else:
            raise FailException("Test Failed - Failed to check installation info")
if __name__ == "__main__":
    unittest.main()
