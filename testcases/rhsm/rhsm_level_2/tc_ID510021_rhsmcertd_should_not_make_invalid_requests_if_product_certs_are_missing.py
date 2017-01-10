from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510021_rhsmcertd_should_not_make_invalid_requests_if_product_certs_are_missing(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # move product cert
            self.move_product_cert()

            # register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # clean rhsm.log
            self.clear_file_content('/var/log/rhsm/rhsm.log')

            # restart certd service
            self.restart_rhsmcertd()

            # check log
            cmd = 'cat /var/log/rhsm/rhsm.log'
            (ret, output) = self.runcmd(cmd, "check log")
            if ret ==0 and '' == output.strip():
                logger.info("It's successful to check log")
            else:
                raise FailException("Test Failed - Failed to check log")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_cert()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def move_product_cert(self):
        cmd = 'mv /etc/pki/product-default/69.pem /root/'
        (ret, output) = self.runcmd(cmd, "move product cert")
        if ret ==0:
            logger.info("It's successful to move product cert")
        else:
            raise FailException("Test Failed - Failed to move product cert")

    def restore_cert(self):
        cmd = 'mv /root/69.pem /etc/pki/product-default/'
        (ret, output) = self.runcmd(cmd, "restore product cert")
        if ret ==0:
            logger.info("It's successful to restore product cert")
        else:
            raise FailException("Test Failed - Failed to restore product cert")

if __name__ == "__main__":
    unittest.main()
