from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536722_display_the_usage_of_orgs_command(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # check installed status
            info1 = 'Usage: subscription-manager orgs [OPTIONS]'
            info2 = 'Display the organizations against which a user can register a system'
            info3 = '-h, --help            show this help message and exit'
            info4 = '--proxy=PROXY_URL     proxy URL in the form of proxy_hostname:proxy_port'
            info5 = '--proxyuser=PROXY_USER'
            info6 = '--proxypassword=PROXY_PASSWORD'
            info7 = '--username=USERNAME   username to use when authorizing against the server'
            info8 = '--password=PASSWORD   password to use when authorizing against the server'
            info9 = '--serverurl=SERVER_URL'
            info10 = '--insecure'
            cmd = 'subscription-manager orgs --help'
            (ret, output) = self.runcmd(cmd, "check org help")
            if ret == 0 and info1 in output and info2 in output and info3 in output and info4 in output and info5 in output and info6 in output and info7 in output and info8 in output and info9 in output and info10 in output:
                logger.info("It's successful to check org help")
            else:
                raise FailException("Test Failed - Failed to check org help")
            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
