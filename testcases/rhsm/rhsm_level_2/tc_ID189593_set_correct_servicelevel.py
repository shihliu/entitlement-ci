from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID189593_set_correct_servicelevel(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # list the designated service level
            servicelevel = self.get_rhsm_cons("servicelevel")
            cmd = "subscription-manager service-level --list"
            (ret, output) = self.runcmd(cmd, "list service level")
            if ret == 0 and servicelevel.lower() in output.lower():
                logger.info("It's successful to list the service level %s." % servicelevel)
                # set correct service level
                cmd = "subscription-manager service-level --set=%s" % servicelevel
                (ret, output) = self.runcmd(cmd, "set correct service level")
                if ret == 0 and "Service level set to: %s" % servicelevel in output:
                    logger.info("It's successful to set correct service level %s." % servicelevel)
                else:
                    raise FailException("Test Failed - Failed to set correct service level %s." % servicelevel)
            else:
                raise FailException("Test Failed - Failed to list the service level %s." % servicelevel)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()






        
