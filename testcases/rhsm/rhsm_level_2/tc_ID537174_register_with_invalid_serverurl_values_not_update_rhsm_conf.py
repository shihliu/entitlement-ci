from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537174_register_with_invalid_serverurl_values_not_update_rhsm_conf(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Check hostname in conf
            serverurl1 = self.check_hostname_in_conf()

            #Register with invalid server url
            invalid_url = '--org=new --serverurl=https://qianqian.com:443/subscription/'
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            cmd = 'subscription-manager register --username=%s --password=%s %s'%(username, password, invalid_url)
            (ret, output) = self.runcmd(cmd, "register with invalid serverurl")
            if ret != 0 and ('Error: CA certificate for subscription service has not been installed.' in output or 'Unable to reach the server at' in output):
                logger.info("It's successful to check registration with invalid serverurl")
            else:
                raise FailException("Test Failed - Failed to check registration with invalid serverurl")

            # Check hostname in conf
            serverurl2 = self.check_hostname_in_conf()
            if serverurl1 == serverurl2:
                logger.info("It's successful to verify that serverurl is not updated after registration with invalid serverurl")
            else:
                raise FailException("Test Failed - Failed to verify that serverurl is not updated after registration with invalid serverurl")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_hostname_in_conf(self):
        cmd = "grep 'hostname = ' /etc/rhsm/rhsm.conf"
        output = ''
        (ret, output) = self.runcmd(cmd, "check org info")
        return output.strip()
        if ret == 0 and orgid in output:
            logger.info("It's successful to check org info by identity")
        else:
            raise FailException("Test Failed - Failed to check org info by identity")

if __name__ == "__main__":
    unittest.main()
