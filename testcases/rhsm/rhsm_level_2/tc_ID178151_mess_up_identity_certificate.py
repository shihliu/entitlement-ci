"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID178151_mess_up_identity_certificate(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            
            # edit the cert.pem
            self.mess_recover_cert('/etc/pki/consumer/cert.pem', 'mess1')
            self.list_availalbe('mess1')
            self.mess_recover_cert('/etc/pki/consumer/cert.pem', 'recover')
            self.list_availalbe('recover')
            
            # edit the key.pem
            self.mess_recover_cert('/etc/pki/consumer/key.pem', 'mess2')
            self.list_availalbe('mess2')
            self.mess_recover_cert('/etc/pki/consumer/key.pem', 'recover')
            self.list_availalbe('recover')
            
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.clean_certs()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def mess_recover_cert(self, cert, direct):
        if direct == 'mess1':
            cmd = 'sed -i "s/-----BEGIN CERTIFICATE-----/-----BEGIN CERTIFICATE-----\\nQQQQQ/g" %s' % cert
        elif direct == 'mess2':
            cmd = 'sed -i "s/-----BEGIN RSA PRIVATE KEY-----/-----BEGIN RSA PRIVATE KEY-----\\nQQQQQ/g" %s' % cert
        elif direct == 'recover':
            cmd = 'sed -i "/QQQQQ/d" %s' % cert
        else:
            raise FailException("Test Failed - error happened to identify the command to run")
        (ret, output) = self.runcmd(cmd, "edit the identity cert")
        if ret == 0:
            logger.info("It's successful to %s the %s" % (direct, cert))
        else:
            raise FailException("Test Failed - error happened to edit the cert")

    def list_availalbe(self, direct):
        cmd_list = "subscription-manager list --available"
        (ret, output) = self.runcmd(cmd_list, "list the available subscriptions")
        if ret != 0:
            if(direct == 'mess1' and ("This system is not yet registered" in output)) or (direct == 'mess2' and ("bad base64 decode" in output)):
                logger.info("It's successful to verify that no subscription is available with changed identity cert!")
        elif direct == 'recover' and ret == 0:
                logger.info("It's successful to verify that available subscription is listed with recovered identity cert!")
        else:
            raise FailException("Test Failed - error happened when list available subscriptions")

    def clean_certs(self):
        cmd = 'subscription-manager clean'
        (ret, output) = self.runcmd(cmd, "clean the certs so that the test case will not influence other cases")
        if ret == 0 and 'All local data removed' in output:
            logger.info("It's successful to clean the certs to make sure that the test case will not influence other cases")
        else:
            raise FailException("Test Failed - error happened when clean certs, please clean them manually to make sure that the test case will not influence other cases")

if __name__ == "__main__":
    unittest.main()
