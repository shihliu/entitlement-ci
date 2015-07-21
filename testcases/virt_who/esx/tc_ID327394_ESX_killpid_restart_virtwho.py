from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID327394_ESX_killpid_restart_virtwho(VIRTWHOBase):
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
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -b -d" %(esx_owner,esx_env,esx_server,esx_username,esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with -b -d")
            if ret == 0:
                logger.info("Succeeded to execute virt-who with -b -d ")
            else:
                raise FailException("Failed to execute virt-who with -b -d")

            #3). check virt-who status
            self.vw_check_virtwho_status_new("running")

            #4). check the status of virt-who
            cmd = "ps -ef | grep -E 'virtwho|virt-who' | grep -v grep"
            ret, output = self.runcmd(cmd, "check the process of virt-who with background mode")
            if ret == 0 and (("virtwho.py" in output) or ("virt-who.py" in output)):
                logger.info("Succeeded to check virt-who process.")
            else:
                raise FailException("Failed to check virt-who process.")

            #5). kill all virt-who process
            cmd = "pidof virtwho.py | xargs kill 9"
            ret, output = self.runcmd(cmd, "kill all the process of virt-who.")
            if ret == 0:
                logger.info("Succeeded to kill virt-who process.")
            else:
                raise FailException("Failed to kill virt-who process.")

            #6). restart virt-who service and check status
            self.vw_restart_virtwho_new()
            self.vw_check_virtwho_status_new("running")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
