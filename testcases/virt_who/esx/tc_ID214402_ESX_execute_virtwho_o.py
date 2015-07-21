from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID214402_ESX_execute_virtwho_o(VIRTWHOBase):
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
            self.vw_stop_virtwho_new()

            #2). Execute virt-who in the -b -d.
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -o -d" %(esx_owner,esx_env,esx_server,esx_username,esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with -o -d")
            if ret == 0:
                logger.info("Succeeded to execute virt-who with -o -d ")
            else:
                raise FailException("Failed to execute virt-who with -o -d")

            #3). check the status of virt-who, shoud no any virt-who process because the one-shot mode! 
            cmd = "ps -ef | grep -E 'virtwho|virt-who' |grep -v grep"
            ret, output = self.runcmd(cmd, "check the process of virt-who with background mode")
            if ret != 0 and "virtwho.py" not in output and "virt-who.py" not in output:
                logger.info("All the virt-who processes exit successfully!")
            else:
                raise FailException("Failed to stop virt-who process.")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
