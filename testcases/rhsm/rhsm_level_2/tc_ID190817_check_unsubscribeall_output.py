from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID190817_check_unsubscribeall_output(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # run cmd unsubscribe --all
            cmd = "subscription-manager unsubscribe --all"
            (ret, output) = self.runcmd(cmd, "run cmd unsubscribe --all")
            expectoutput = "This machine has been unsubscribed from 1 subscriptions"
            expectoutputnew = "subscription removed from this system."
            expectoutput5101 = "subscription removed at the server."
            expectoutput5102 = "local certificate has been deleted."
            if 0 == ret and ((expectoutput5101 in output and expectoutput5102 in output) or (expectoutput in output or expectoutputnew in output)):
                firstresult = True
                print "True\n"
            else:
                firstresult = False
                print "False\n"
            # unsubscribe before subscribe
            cmd = "subscription-manager unsubscribe --all"
            (ret, output) = self.runcmd(cmd, "run cmd unsubscribe --all again")
            expectoutput = "This machine has been unsubscribed from 0 subscriptions"
            expectoutputnew = "0 subscriptions removed from this system."
            expectoutput510 = "subscriptions removed at the server."
            if 0 == ret and (expectoutput510 in output or expectoutput in output or expectoutputnew in output):
                secondresult = True
                print "True\n"
            else:
                secondresult = False
                print "False\n"
            if firstresult and secondresult:
                logger.info("It is successful to run cmd subscription-manager unsubscribe --all and check the output!")
            else:
                raise FailException("Test Faild - Failed to run cmd subscription-manager unsubscribe --all and check the output!")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
