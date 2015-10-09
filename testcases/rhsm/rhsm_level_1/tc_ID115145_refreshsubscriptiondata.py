from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID115145_refreshsubscriptiondata(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # get serialnumlist before remove local subscription data
            serialnumlist_pre = self.get_subscription_serialnumlist()
            # rm the subscription data
            cmd = "rm -f /etc/pki/entitlement/*"
            (ret, output) = self.runcmd(cmd, "remove local entitlement cert")
            if ret == 0:
                logger.info("It's successful to remove all local subscription data.")
            else:
                raise FailException("Test Failed - It's failed to remove all local subscription data.")
            # refresh subscription data from candlepin server
            cmd = "subscription-manager refresh"
            (ret, output) = self.runcmd(cmd, "refresh subscriptions data")
            if ret == 0 and "All local data refreshed" in output:
                # get serialnumlist after refresh subscription data from server
                serialnumlist_post = self.get_subscription_serialnumlist()
                if len(serialnumlist_post) == len(serialnumlist_pre) and serialnumlist_post.sort() == serialnumlist_pre.sort():
                    logger.info("It's successful to refresh all subscription data from server.")
                else:
                    raise FailException("Test Failed - It's failed to refresh all subscription data from server.") 
            else:
                raise FailException("Test Failed - Failed to refresh all subscription data from server.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
