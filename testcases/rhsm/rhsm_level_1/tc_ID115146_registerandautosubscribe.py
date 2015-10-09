from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID115146_registerandautosubscribe(RHSMBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            try:
                username = self.get_rhsm_cons("username")
                password = self.get_rhsm_cons("password")
                # productid = RHSMConstants.get_constant("productid")
                # autosubprod = self.get_rhsm_cons("autosubprod")
                # remove check (autosubprod in output) since rhel 7 changed
                cmd = "subscription-manager register --username=%s --password=%s --autosubscribe" % (username, password)
                (ret, output) = self.runcmd(cmd, "register and auto-subscribe")
                if ret == 0:
                    if (("The system has been registered with ID" in output) or ("The system has been registered with id" in output)) and ("Subscribed" in output) and ("Not Subscribed" not in output):
                        if self.sub_checkidcert():
                            logger.info("It's successful to register.")
                        else:
                            raise FailException("Test Failed - Failed to register.")
                    else:
                        raise FailException("Test Failed - Failed to register and auto-subscribe correct product.")
                else:
                    raise FailException("Test Failed - Failed to register and auto-subscribe.")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
