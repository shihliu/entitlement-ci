from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536758_register_with_org_option_via_cli(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Check consumer cert before registration
            certs_before = self.check_consumer_cert()
            if certs_before.strip() == '':
                logger.info("It's successful to verify that no consumer cert installed before registration")
            else:
                raise FailException("Test Failed - Failed to verify that no consumer cert installed before registration")

            #Register with valid org
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            valid_org = self.get_rhsm_cons("default_org")
            cmd = 'subscription-manager register --username=%s --password=%s --org=%s'%(username, password, valid_org)
            (ret, output) = self.runcmd(cmd, "register with valid org")
            if ret == 0 and "The system has been registered with ID:" in output:
                logger.info("It's successful to check registration with valid org")
            else:
                raise FailException("Test Failed - Failed to check registration with valid org")

            # Check consumer cert after registration
            certs_after = self.check_consumer_cert()
            if 'cert.pem' in certs_after and 'key.pem' in certs_after:
                logger.info("It's successful to verify that no consumer cert installed after registration")
            else:
                raise FailException("Test Failed - Failed to verify that no consumer cert installed after registration")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_consumer_cert(self):
        output=''
        cmd = 'ls /etc/pki/consumer/'
        (ret, output) = self.runcmd(cmd, "check consumer cert")
        return output
        if ret == 0:
            logger.info("It's successful to check consumer cert")
        else:
            raise FailException("Test Failed - Failed to check consumer cert")

if __name__ == "__main__":
    unittest.main()
