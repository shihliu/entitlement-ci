from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509859_the_count_of_subscriptions_removed_should_not_zero_after_certs_are_imported_successfully(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # make valid entitlement cert
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            productid = self.get_rhsm_cons("productid")
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            cmd = 'cat /etc/pki/entitlement/* > /tmp/test.pem'
            (ret, output) = self.runcmd(cmd, "prepare a valid pem file")
            if ret == 0:
                logger.info("It's successful to prepare a valid pem file.")
            else :
                raise FailException("Test Failed - error happened when prepare a invalid pem file")

            # make sure the system is unregistered before import cert.
            self.sub_unregister()

            # import the valid cert
            cmd = "subscription-manager import --certificate=/tmp/test.pem"
            (ret, output) = self.runcmd(cmd, "import exist entitlement certificate") 
            if ret == 0 and "Successfully imported certificate" in output:
                logger.info("Import existing entitlement certificate successfully.")
            else:
                raise FailException("Test Failed - Failed to import entitlement certificate.")

            # Remove all the imported subscriptions
            cmd = 'subscription-manager remove --all'
            (ret, output) = self.runcmd(cmd, "remove imported subscriptions")
            if ret ==0 and '1 subscriptions removed from this system' in output:
                logger.info("It's successful to remove imported subscriptions by ignoring bug 1371472")
            else:
                raise FailException("Test Failed - Failed to remove imported subscriptions")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.runcmd('rm -f /tmp/test.pem', "remove test cert")
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
