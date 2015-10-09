from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID126354_import_invalid_entitlement_cert_via_CLI(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            productid = self.get_rhsm_cons("productid")
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            cmd = 'cat /etc/pki/entitlement/*.pem > /home/foo.pem'
            (ret, output) = self.runcmd(cmd, "prepare a invalid pem file")
            if ret == 0:
                # unsubscribe
                cmd = 'subscription-manager unsubscribe --all'
                (ret, output) = self.runcmd(cmd, "unsubscribe")
                if ret == 0 and "removed at the server" in output:
                    logger.info("It's successful to remove all subscriptions")
                else:
                    raise FailException("Test Failed - Failed to remove subscriptions.")
                # import certs
                cmd = 'subscription-manager import --certificate=/home/foo.pem'
                (ret, output) = self.runcmd(cmd, "import certs")
                if ret == 0 and "Successfully imported certificate" in output:
                    logger.info("It's successful to import certs")
                else:
                    raise FailException("Test Failed - Failed to import certs.")
                # check consumed status
                cmd = 'subscription-manager list --consumed'
                (ret, output) = self.runcmd(cmd, "list consumed subscriptions")
                if ret == 0 and "Consumed Subscriptions" in output:
                    logger.info("It's successful to verify importing invalid entitlement cert via CLI")
                else:
                    raise FailException("Test Failed - Failed to verify importing invalid entitlement cert via CLI.")
            else:
                raise FailException("Test Failed - error happened when import certs.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            cmd = 'rm -rf /home/foo.pem'
            (ret, output) = self.runcmd(cmd, "remove /home/foo.pem file")
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % __name__)

if __name__ == "__main__":
    unittest.main()
