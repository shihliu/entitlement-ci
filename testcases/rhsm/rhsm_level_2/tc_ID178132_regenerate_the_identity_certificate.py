"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""
from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID178132_regenerate_the_identity_certificate(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            
            # check identity and record the identity information
            cmd_check = "subscription-manager identity"
            (ret, output) = self.runcmd(cmd_check, "run subscription-manager identity")
            identity_info1 = output
            if ret == 0:
                logger.info("It's successful to display identity 1 info!")
            else:
                raise FailException("Test Failed - Failed to display identity 1 info")

            # check cert information
            cmd_check_cert = "stat /etc/pki/consumer/cert.pem | grep -i Modify | awk -F. '{print $1}' | awk '{print $2$3}'| awk -F- '{print $1$2$3}' | awk -F: '{print $1$2$3}'"
            (ret, output) = self.runcmd(cmd_check_cert, "check consumer certs")
            if ret == 0:
                modified_date1 = output
                logger.info("It's successful to gain the certs information and record the modified time for first time!")
            else:
                raise FailException("Test Failed - Failed to display modified info")

            # regenerate the certs
            cmd_regenerate = "subscription-manager identity --regenerate --username=%s --password='%s' --force" % (username, password)
            (ret, output) = self.runcmd(cmd_regenerate, "regenerate the identity certs")
            if ret == 0 and "Identity certificate has been regenerated" in output:
                logger.info("It's successful to regenerate the identity certs")
            else:
                raise FailException("Test Failed - Failed to regenerate the identity certs")
    
            # check identity and record the identity information
            cmd_check = "subscription-manager identity"
            (ret, output) = self.runcmd(cmd_check, "run subscription-manager identity")     
            identity_info2 = output
            if ret == 0:
                logger.info("It's successful to display identity 2 info!")
            else:
                raise FailException("Test Failed - Failed to display identity 2 info")

            # check wether the identity infos are the same
            if identity_info1 == identity_info2:
                logger.info("It's successful to verify that the identity infos are the same")
            else:
                raise FailException("Test Failed - Failed to verify that the identity infos are the same")

            # check cert information
            cmd_check_cert = "stat /etc/pki/consumer/cert.pem | grep -i Modify | awk -F. '{print $1}' | awk '{print $2$3}'| awk -F- '{print $1$2$3}' | awk -F: '{print $1$2$3}'"
            (ret, output) = self.runcmd(cmd_check_cert, "check consumer certs") 
            if ret == 0:
                modified_date2 = output
                logger.info("It's successful to gain the certs information and record the modified time for second time!")
            else:
                raise FailException("Test Failed - Failed to display modified info")
    
            # check wether the certs are renewed
            if int(modified_date2) > int(modified_date1):
                logger.info("It's successful to verify that the certs have been renewed")
            else:
                raise FailException("Test Failed - Failed to verify that the certs have been renewed")

            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()



