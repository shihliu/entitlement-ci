"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID178502_display_accountcontract_number_in_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            
            # record the entitlement cert
            cmd = "ls /etc/pki/entitlement/*.pem | grep -v key.pem"
            (ret, certname0) = self.runcmd(cmd, "get the entitlement cert name")
            if (ret == 0) and (certname0 != None):
                logger.info("It's successful to get the entitlement cert name")
                certname = certname0.strip('\n')
            else:
                raise FailException("Test Failed - Failed to get the entitlement cert name")
            # list consumed subscription, record the account number, and display the account number in entitlement cert
            self.display_number(certname, "Account")
            # list consumed subscription, record the contract number, and display the contract number in entitlement cert
            self.display_number(certname, "Contract")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def display_number(self, certname, numbername):
        # list consumed subscription, record the account number
        cmd = "subscription-manager list --consumed | grep %s" % numbername
        (ret, output) = self.runcmd(cmd, "list consumed subscription and record %s" % numbername)
        number = output.split(':')[1]
        if ret == 0 and number != "":
            logger.info("It's successful to list consumed subscription and record %s." % numbername)
        else:
            raise FailException("Test Failed - It's failed to list consumed subscription and record %s." % numbername)
        # display the number in entitlement cert
        if number.strip() == '':
            logger.info("The %s is empty" % numbername)
        else:
            cmd = "rct cat-cert %s | grep %s" % (certname, number)
            (ret, output1) = self.runcmd(cmd, "check and display the %s number in %s" % (numbername, certname))
            if ret == 0:
                if numbername in output1:
                    logger.info("It's successful to display %s number in %s." % (numbername, certname))
                else:
                    logger.info("%s is not set in %s" % (numbername, certname))
            else:
                raise FailException("Test Failed - It's failed to display %s number in %s." % (numbername, certname))

if __name__ == "__main__":
    unittest.main()
