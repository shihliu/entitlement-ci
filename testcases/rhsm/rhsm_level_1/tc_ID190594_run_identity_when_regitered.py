from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID190594_run_identity_when_regitered(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register the system
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            cmd = 'subscription-manager identity'
            (ret, output) = self.runcmd(cmd, "running identity command")
            if ret == 0 and (('system identity' in output) and ('name' in output) and ('org name' in output) and ('org id' in output or 'org ID' in output)):
                logger.info("It's successful to check the output of identity command when the machine is registered.") 
            else:
                raise FailException("Test Failed - Failed to check the output of identity command when the machine is registered.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
