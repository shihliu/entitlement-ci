"""******************************************

@author        : shihliu@redhat.com
@date        : 2013-03-11

******************************************"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID181268_import_valid_invaild_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # get env variables
            autosubprod = RHSMConstants().get_constant("autosubprod")
            installedproductname = RHSMConstants().get_constant("installedproductname")
            # create invaild pem file
            cmd = "touch /root/invalid.pem"
            (ret, output) = self.runcmd(cmd, "create invalid pem file")    
            if ret == 0:
                logging.info(" It's successful to create invalid pem file.")                
            else:
                raise FailException("Test Failed - Failed to create invalied pem file.")
            # create vaild pem file
            self.sub_autosubscribe(autosubprod)
            cmd = "cat /etc/pki/entitlement/*-key.pem /etc/pki/entitlement/*.pem > /root/valid.pem"    
            (ret, output) = self.runcmd(cmd, "Create valid pem file")            
            if ret == 0 :
                logging.info("It's successful to create valid cert file.")
            else:
                raise FailException("Test Failed - Failed to create valid cert file.")
            # Unsubscribe all product
            cmd = "subscription-manager unsubscribe --all"
            (ret, output) = self.runcmd(cmd, "Unsubscribe all products")
            if ret == 0 :
                self.list_noconsumed_subscriptions()
            else :
                raise FailException("Test Failed - Failed to unsubscribe all product.")
            # Import more two certificates
            cmd = "subscription-manager import --certificate=/root/valid.pem --certificate=/root/invalid.pem"
            (ret, output) = self.runcmd(cmd, "import valid and invalid pem files")
            if ("Successfully" in output) and ("not a valid certificate file" in output):
                logging.info("It's successful to check import two certificates.")
            else:
                raise FailException("Test Failed - Failed to check import two certificates.")
            # Check the import result
            self.list_consumed_subscriptions(installedproductname)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.remove_certfile()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_noconsumed_subscriptions(self):
        cmd = "subscription-manager list --consumed"
        (ret, output) = self.runcmd(cmd, "no consumed subscriptions in list")
        output_join = " ".join(x.strip() for x in output.split())
        if ret == 0 and (("No consumed" in output) or ("No consumed" in output_join)):
            logging.info("It's successful to check no consumed subscriptions.")
            return True
        else:
            raise FailException("Test Failed - Failed to check no consumed subscriptions.")
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

    def remove_certfile(self):
        cmd = "rm -rf /root/*.pem"
        (ret, output) = self.runcmd(cmd, "Remove all pem file under /root")
        if ret == 0 :
            logging.info("It's successful to remove all pem file under /root.")
            return True
        else:
            raise FailException("Test Failed - Failed to Remove all pem file under /root.")
            return False    

if __name__ == "__main__":
    unittest.main()
