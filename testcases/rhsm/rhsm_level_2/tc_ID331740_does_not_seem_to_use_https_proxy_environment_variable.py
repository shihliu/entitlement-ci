from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID331740_does_not_seem_to_use_https_proxy_environment_variable(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            samhostip = RHSMConstants().samhostip
            if samhostip != None:
                logger.info("sam not test proxy")
            else:
                # check the the rhsm conf file for proxy before register with proxy
                self.check_proxy_rhsm()
                # register with specified proxy
                cmd = "https_proxy=squid.corp.redhat.com:3128 subscription-manager register --username=%s --password='%s'" % (username, password)
                (ret, output) = self.runcmd(cmd, "register with proxy")
                if ret == 0 and "The system has been registered with ID" in output:
                    logger.info("It's successful to register with proxy")
                else:
                    raise FailException("Test Failed - Failed to register with proxy.")
                # check the the rhsm conf file for proxy after register with proxy
                self.check_proxy_rhsm()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_proxy_rhsm(self):
        cmd = "cat /etc/rhsm/rhsm.conf | egrep 'proxy_hostname|proxy_port'"
        (ret, output) = self.runcmd(cmd, "check_proxy_rhsm")
        o1 = output.split("\n")[0].split("=")[1]
        o2 = output.split("\n")[1].split("=")[1]
        if ret == 0 and o1 == '' and o2 == '':
            logger.info("It's successful to check that Environment variable not written into conf file")
        else:
            raise FailException("Test Failed - Failed to check that Environment variable not written into conf file.")

if __name__ == "__main__":
    unittest.main()
