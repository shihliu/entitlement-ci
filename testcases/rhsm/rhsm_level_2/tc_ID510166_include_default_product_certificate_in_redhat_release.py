from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510166_include_default_product_certificate_in_redhat_release(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # list installed product id
            installedpro = self.list_installed_product()

            # list product cert in /etc/pki/product
            cert_pro_path = self.list_product('/etc/pki/product')

            # list product cert in /etc/pki/product-default
            cert_default_path = self.list_product('/etc/pki/product-default')

            if cert_pro_path == '' and installedpro == cert_default_path:
                logger.info("It's successful to check default product")
            else:
                raise FailException("Test Failed - Failed to check default product")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_product(self, productpath):
        productcert = ''
        cmd = 'ls %s'%productpath
        (ret, output) = self.runcmd(cmd, "list product")
        if ret ==0:
            productcert = output.strip().split('.')[0]
            logger.info("It's successful to list product")
        else:
            raise FailException("Test Failed - Failed to list product")
        return productcert

    def list_installed_product(self):
        productid = ''
        cmd = 'subscription-manager list --installed | grep "Product ID"'
        (ret, output) = self.runcmd(cmd, "get product id")
        if ret ==0:
            productid = output.strip().split(':')[1].strip()
            logger.info("It's successful to get product id")
        else:
            raise FailException("Test Failed - Failed to get product id")
        return productid

if __name__ == "__main__":
    unittest.main()
