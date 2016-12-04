from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID189594_servicelevel_name_insensitive(RHSMBase):
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
            (ret, output) = self.runcmd(cmd, "list correct service level")
            if ret == 0 and ("servicelevel" or "Service Levels" in output):
                logger.info("It's successful to list the service level %s." % servicelevel)
                # get a customized service level with lowercase and capital
                slabegin = servicelevel[:3].upper()
                slaend = servicelevel[3:].lower()
                servicelevel = slabegin + slaend
                cmd = "subscription-manager service-level --set=%s" % servicelevel
                (ret, output) = self.runcmd(cmd, "set a customized service level with lowercase and capital")
                if ret == 0 and "Service level set to: %s" % servicelevel in output:
                    logger.info("It is successful to verify service level is insensitive to lowercase and capital.")
                else:
                    raise FailException("Test Failed - Failed to verify service level is insensitive to lowercase and capital.")
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
