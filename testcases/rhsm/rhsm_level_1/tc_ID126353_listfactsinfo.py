from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID126353_listfactsinfo(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)

            cmd = "subscription-manager facts --list"
            (ret, output) = self.runcmd(cmd, "list facts")
            if ret == 0 and "system.certificate_version" in output and "virt.is_guest" in output and "virt.host_type" in output:
                logger.info("It's successful to list facts")
                if "system.certificate_version: 3." in output:
                    logger.info("It's successful to check cert v3")
                else:
                    FailException("Test Failed - Failed to check cert v3.")
                if "virt.is_guest: True" in output and "virt.host_type: kvm" in output:
                    logger.info("It's successful to check the machine is kvm virtual")
                elif "virt.is_guest: False" in output and "virt.host_type: Not Applicable" in output:
                    logger.info("It's successful to check the machine is physical")
                else:
                    FailException("Test Failed - Failed to check virtual or physical.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % __name__)

if __name__ == "__main__":
    unittest.main()
