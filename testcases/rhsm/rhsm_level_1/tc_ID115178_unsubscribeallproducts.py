from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID115178_unsubscribeallproducts(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # unsubscribe all products
            cmd = "subscription-manager unsubscribe --all"
            (ret, output) = self.runcmd(cmd, "unsubscribe")
            expectout = "This machine has been unsubscribed from"
            # for rhel6.4 new output version
            expectoutnew64 = "subscription removed from this system."
            # for rhel5.10 new output version
            expectoutnew510 = "subscription removed at the server."
            if ret == 0 and (expectout in output or expectoutnew510 in output or expectoutnew64 in output):
                if len(os.listdir('/etc/pki/entitlement')) <= 0:
                    logger.info("It's successful to unsubscribe from all products.")
                else:
                    raise FailException("Test Failed - The information shown that it's failed to unsubscribe from all products.")
            else:
                raise FailException("Test Failed - Failed to unsubscribe from all products.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
