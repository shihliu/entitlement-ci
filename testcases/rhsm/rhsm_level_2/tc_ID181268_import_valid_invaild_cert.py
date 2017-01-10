"""******************************************

@author        : shihliu@redhat.com
@date        : 2013-03-11

******************************************"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID181268_import_valid_invaild_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # make invalid entitlement cert
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            productid = self.get_rhsm_cons("productid")
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            cmd = 'cat /etc/pki/entitlement/*key.pem > /root/invalid.pem;cat /etc/pki/entitlement/* > /root/valid.pem'
            (ret, output) = self.runcmd(cmd, "prepare a valid pem file and an invalid one.")
            if ret == 0:
                logger.info("It's successful to prepare a valid pem file.")
            else :
                raise FailException("Test Failed - error happened when prepare a invalid pem file")

            # get consumed subscription's sku to compare later.
            sku1 = self.get_consumed_sku()
            print 'sku1:%s'%sku1

            # make sure the system is unregistered before import cert.
            self.sub_unregister()

            # import the valid cert
            cmd = "subscription-manager import --certificate=/root/valid.pem --certificate=/root/invalid.pem"
            (ret, output) = self.runcmd(cmd, "import exist entitlement certificate") 
            if ret == 0 and "invalid.pem is not a valid certificate file. Please use a valid certificate" in output and 'Successfully imported certificate valid.pem' in output:
                logger.info("Import existing entitlement certificate successfully and invalid cert is not imported.")
            else:
                raise FailException("Test Failed - Failed to import entitlement certificate.")

            # check consumed status
            sku2 = self.get_consumed_sku()
            print 'sku2:%s'%sku2
            if sku1 == sku2:
                logger.info("It's successful to check corresponding subscription.")
            else:
                raise FailException("Test Failed - error happened when check corresponding subscription.")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.runcmd('rm -f /root/*valid.pem', "remove test cert")
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def get_consumed_sku(self):
        cmd = "subscription-manager list --consumed | grep 'SKU'"
        (ret, output) = self.runcmd(cmd, "check sku in the list consumed subscriptions")
        if ret == 0:
            return output.strip().split("\n")[0].split(":")[1].strip()
            logger.info("It's successful to get consumed sku.")
        else:
            return None
            raise FailException("Test Failed - error happened get consumed sku.")

if __name__ == "__main__":
    unittest.main()
