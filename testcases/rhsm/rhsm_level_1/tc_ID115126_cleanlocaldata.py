from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID115126_cleanlocaldata(RHSMBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                self.sub_register(username, password)
                # [A] - prepare test env
                # get uuid of consumer
                cmd = "subscription-manager identity | grep identity"
                (ret, output) = self.runcmd(cmd, "get identity")
                uuid = output.split(':')[1].strip()
                productid = self.get_rhsm_cons("productid")
                autosubprod = self.get_rhsm_cons("autosubprod")
                self.sub_autosubscribe(autosubprod)
                # [B] - run the test
                # clean local consumer and subscription data
                cmd = "subscription-manager clean"
                (ret, output) = self.runcmd(cmd, "clean local data")
                if ret == 0 and ("All local data removed" in output):
                    cmd1 = 'ls /etc/pki/consumer/'
                    cmd2 = 'ls /etc/pki/entitlement/'
                    (ret1, output1) = self.runcmd(cmd1, "list what's in the consumer folder")
                    (ret2, output2) = self.runcmd(cmd2, "list what's in the entitlement folder")
                    if ret1 == 0 and output1 == '' and ret2 == 0 and output2 == '':
                        logger.info("It's successful to clean local consumer and entitlement information")
                    else:
                        raise FailException("Test Failed - The information shows that it's failed to clean local data.")
                else:
                    raise FailException("Test Failed - The information shows that it's failed to clean local data---return code or output is wrong.")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
