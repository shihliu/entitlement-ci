from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537151_access_cdn_contents_through_thumbslug_without_entitlement_certificates(RHSMBase):
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

                # remove entitlement certs
                cmd = 'rm -rf /etc/pki/entitlement'
                (ret, output) = self.runcmd(cmd, "remove ent certs")
                if ret == 0:
                    logger.info("It's successful to remove ent certs")
                else:
                    raise FailException("Test Failed - Failed to remove ent certs")

                # check pkg installation status
                revoke_info1 = 'This system is registered to Red Hat Subscription Management, but is not receiving updates. You can use subscription-manager to assign subscriptions.'
                revoke_info2 = 'This system is registered with an entitlement server, but is not receiving updates. You can use subscription-manager to assign subscriptions.'
                revoke_status = self.check_installation()
                if revoke_info1 or revoke_info2 in revoke_status:
                    logger.info("It's successful to verify that system should not be able to access CDN bits through thumbslug proxy")
                else:
                    raise FailException("Test Failed - Failed to verify that system should not be able to access CDN bits through thumbslug proxy")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
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
