from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID322866_ESX_run_virtwho_with_sam_option(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_owner = VIRTWHOConstants().get_constant("VIRTWHO_ESX_OWNER")
            esx_env = VIRTWHOConstants().get_constant("VIRTWHO_ESX_ENV")
            esx_server = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
            esx_username = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
            esx_password = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")

            #1). stop virt-who service
            self.vw_stop_virtwho()

            #2). Execute virt-who in the one-shot mode.
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s --sam -d -o" %(esx_owner,esx_env,esx_server,esx_username,esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with --sam -d -o")
            if ret == 0 and "DEBUG" in output and "ERROR" not in output:
                logger.info("Succeeded to execute virt-who with --sam -d -o")
            else:
                raise FailException("Failed to execute virt-who with --sam -d -o")

            #3).restart virtwho service
            self.vw_restart_virtwho()

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
