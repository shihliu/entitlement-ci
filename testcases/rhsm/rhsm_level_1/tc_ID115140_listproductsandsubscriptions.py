from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115140_listproductsandsubscriptions(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # list installed products
            installedproductname = RHSMConstants().get_constant("installedproductname")
            self.list_installed_products(installedproductname)
            # list consumed subscriptions
            self.list_consumed_subscriptions(installedproductname)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_installed_products(self, expectedproductname):
        if "," in expectedproductname:
            productnamelist = expectedproductname.split(",")
        else:
            productnamelist = [expectedproductname]
        cmd = "subscription-manager list --installed"
        (ret, output) = self.runcmd(cmd, "list installed products")
        # This line for rhel6.4 new output version
        output_join = " ".join(x.strip() for x in output.split())
        if ret == 0:
            for productname in productnamelist:
                if (productname in output or productname in output_join):
                    logging.info("It's successful to list installed product %s." % (productname))
                    return True
                else:
                    raise FailException("Test Failed - The product %s is not installed." % (productname))
                    return False
        else:
            raise FailException("Test Failed - Failed to list installled products.")
            return False

    def list_consumed_subscriptions(self, installedproductname):
        cmd = "subscription-manager list --consumed"
        (ret, output) = self.runcmd(cmd, "list consumed subscriptions")
        output_join = " ".join(x.strip() for x in output.split())
        if ret == 0 and ((installedproductname in output) or (installedproductname in output_join)):
            logging.info("It's successful to list all consumed subscriptions.")
            return True
        else:
            raise FailException("Test Failed - Failed to list all consumed subscriptions.")
            return False

if __name__ == "__main__":
    unittest.main()


