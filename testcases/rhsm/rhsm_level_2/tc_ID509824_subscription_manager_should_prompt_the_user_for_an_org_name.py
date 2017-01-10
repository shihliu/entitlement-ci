from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509824_subscription_manager_should_prompt_the_user_for_an_org_name(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if not self.skip_stage_check():
            try:
                Org = self.get_rhsm_cons('default_org')
                cmd1 = "subscription-manager register --org=%s" % Org
                # Register
                (ret, output) = self.runcmd_interact(cmd1, "register with credentials prompts")
                if ret == 0 and "The system has been registered with ID:" in output:
                    logger.info("It's successful to register with credentials prompts")
                    self.sub_unregister()
                else:
                    raise FailException("Test Failed - Failed to register with credentials prompts")

                # Register with auto-attach
                cmd2 = "subscription-manager register --auto-attach --org=%s" % Org
                (ret, output) = self.runcmd_interact(cmd2, "register and auto-attach with credentials prompts")
                if ret == 0 and "The system has been registered with ID:" in output and "Subscribed" in output and "Not Subscribed" not in output:
                    logger.info("It's successful to register and auto-attach with credentials prompts")
                else:
                    raise FailException("Test Failed - Failed to register and auto-attach with credentials prompts")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
