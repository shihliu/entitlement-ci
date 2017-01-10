from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509869_include_dash_in_the_msgid_as_a_prefix_to_auto_attach_interval(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
#            username = self.get_rhsm_cons("username")
#            password = self.get_rhsm_cons("password")
#            self.sub_register(username, password)
#            autosubprod = self.get_rhsm_cons("autosubprod")
#            self.sub_autosubscribe(autosubprod)
            cmd = "rhsmcertd --help | grep heal-interval"
            (ret, output) = self.runcmd(cmd, "run rhsmcertd --help")
            if ret == 0 and ("deprecated, see --auto-attach-interval" in output):
                logger.info("two dashs before the auto-attach-interval")
            else:
                raise FailException("Test Failed - no two dashs before the auto-attach-interval")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
