from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID510150_error_parsing_baseurl_should_be_informative(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'subscription-manager register --baseurl=http://'
            (ret, output) = self.runcmd(cmd, "check error parsing baseurl 1")
            if ret !=0 and 'Server URL is just a schema. Should include hostname, and/or port and path' in output:
                logger.info("It's successful to check error parsing baseurl 1")
            else:
                raise FailException("Test Failed - Failed to check error parsing baseurl 1")

            cmd = 'subscription-manager register --baseurl=https://hostname:PORT/prefix'
            (ret, output) = self.runcmd(cmd, "check error parsing baseurl 2")
            if ret !=0 and 'Server URL port should be numeric' in output:
                logger.info("It's successful to check error parsing baseurl 2")
            else:
                raise FailException("Test Failed - Failed to check error parsing baseurl 2")

            cmd = 'subscription-manager register --baseurl=https://hostname:/prefix'
            (ret, output) = self.runcmd(cmd, "check error parsing baseurl 3")
            if ret !=0 and 'Server URL port should be numeric' in output:
                logger.info("It's successful to check error parsing baseurl 3")
            else:
                raise FailException("Test Failed - Failed to check error parsing baseurl 3")

            cmd = 'subscription-manager register --baseurl=https:/hostname'
            (ret, output) = self.runcmd(cmd, "check error parsing baseurl 4")
            if ret !=0 and 'Server URL has an invalid scheme. http:// and https:// are supported' in output:
                logger.info("It's successful to check error parsing baseurl 4")
            else:
                raise FailException("Test Failed - Failed to check error parsing baseurl 4")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
