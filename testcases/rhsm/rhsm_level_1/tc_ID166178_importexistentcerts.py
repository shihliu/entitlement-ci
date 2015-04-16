from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID166178_importexistentcerts(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # check whether entitlement certificates generated and productid in them or not
            productid = self.check_sku_in_consumed_subscriptions()
            self.sub_checkentitlementcerts(productid)
            # generate entitlement certificate to import and remove entitlement certificate
            self.generate_and_remove_entcert()
            # import existing entitlement cert
            self.import_exist_entcert()
            # check whether entitlement certificates generated and productid in them or not
            self.sub_checkentitlementcerts(productid)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.runcmd('rm -f /tmp/test.pem', "remove test cert")
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_sku_in_consumed_subscriptions(self):
        sku = None
        cmd = "subscription-manager list --consumed | grep 'SKU'"
        (ret, output) = self.runcmd(cmd, "check sku in the list consumed subscriptions")
        print "output: \n", output[0]
        if ret == 0:
            sku = output.split(":")[1].strip()
            return sku
        else :
            return sku
            raise FailException("Test Failed - error happened when check sku in the list consumed subscriptions")

    def generate_and_remove_entcert(self):
        cmd = "cat /etc/pki/entitlement/* > /tmp/test.pem"
        (ret, output) = self.runcmd(cmd, "generate entitlement cert")
        if ret == 0:
            self.runcmd('rm -f /etc/pki/entitlement/*', "remove entitlement cert")
        else :
            raise FailException("Test Failed - error happened when generate entitlement certs")

    def import_exist_entcert(self):
        cmd = " subscription-manager import --certificate=/tmp/test.pem"
        (ret, output) = self.runcmd(cmd, "import exist entitlement certificate") 
        if ret == 0 and "Successfully imported certificate" in output:
            logger.info("Import existing entitlement certificate successfully.")
        else:
            raise FailException("Test Failed - Failed to import entitlement certificate.")

if __name__ == "__main__":
    unittest.main()
