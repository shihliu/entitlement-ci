from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID147112_register_and_autosubscribe_with_specific_SLA(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            service_level = self.get_rhsm_cons("servicelevel")
            # register and auto subscribe with one service level
            cmd="subscription-manager register --username=%s --password=%s --autosubscribe --servicelevel=%s" %(username, password, service_level)
            (ret,output)=self.runcmd(cmd,"register and autosubscribe with one specific service-level")
            if ret == 0 and (("The system has been registered with ID" in output) or ("The system has been registered with id" in output)) and \
                (("Status:Subscribed" in output) or re.search("Status:\s+Subscribed", output)):
                logger.info("It's successful to do register and autosubscribe with one service-level: %s."%service_level)
            else:
                raise FailException("Test Failed - Failed to register and auto subscribe with one service level.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
