from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537227_subs_man_attach_auto_will_not_persist_unsetting_of_service_level(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register and auto-attach
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # set service-level
            service_level = self.get_rhsm_cons("servicelevel")
            self.sub_set_servicelevel(service_level)
            if service_level in self.check_sla():
                logger.info("It's successful to set service level")
            else:
                raise FailException("Test Failed - Failed to set service level")

            # disable autoheal
            self.disable_autoheal()

            # auto attach with service level unset
            cmd = 'subscription-manager remove --all;subscription-manager attach --auto --servicelevel=""'
            (ret, output) = self.runcmd(cmd, "auto attach with sla unset")
            if ret == 0 and 'Service level set to: \n' in output:
                logger.info("It's successful to auto attach with sla unset")
            else:
                raise FailException("Test Failed - Failed to auto attach with sla unset")

            # check service level
            if self.check_sla() == 'Service level preference not set':
                logger.info("It's successful to check service level unset")
            else:
                raise FailException("Test Failed - Failed to check service level unset")

            # list consumed to check auto assign service level
            cmd = "subscription-manager list --consumed | grep 'Service Level:'"
            (ret, output) = self.runcmd(cmd, "check sla")
            if ret == 0 and output.strip().split(":")[1] != '':
                logger.info("It's successful to check sla auto-assigned")
            else:
                raise FailException("Test Failed - Failed to check sla auto-assigned")
                
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.enable_autoheal()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_sla(self):
        cmd = "subscription-manager service-level"
        (ret, output) = self.runcmd(cmd, "check sla")
        if ret == 0:
            sla = output.strip()
            logger.info("It's successful to check sla")
            return sla
        else:
            raise FailException("Test Failed - Failed to check sla")

if __name__ == "__main__":
    unittest.main()
