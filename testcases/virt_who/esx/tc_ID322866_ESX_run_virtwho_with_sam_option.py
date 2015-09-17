from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID322866_ESX_run_virtwho_with_sam_option(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the hostuuid and guestuuid
            host_uuid = self.esx_get_host_uuid(destination_ip)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1). stop virt-who before run -o -d --sam
            self.service_command("stop_virtwho")

            #2). fetch virt-who cmd with -o -d --sam
            cmd = self.virtwho_cli("esx") + " -o -d --sam "

            #3). run virt-who with -o -d --sam 
            ret, output = self.runcmd(cmd, "executing virt-who with -o -d --sam")
            if ret == 0 and output is not None and "ERROR" not in output and host_uuid in output and guestuuid in output:
                logger.info("Succeeded to run virt-who with -o -d --sam,  can find uuid from oneshot log message.")
            else:
                raise FailException("Failed to run virt-who with -o -d --sam, can't find uuid from oneshot log meesage.")

            #4). check the status of virt-who, shoud no any virt-who process because the one-shot mode! 
            cmd = "ps -ef | grep -E 'virtwho|virt-who' |grep -v grep"
            ret, output = self.runcmd(cmd, "check the process of virt-who with -o -d --sam")
            if ret != 0 and "virtwho.py" not in output and "virt-who.py" not in output:
                logger.info("All the virt-who processes exit successfully!")
            else:
                raise FailException("Failed to stop virt-who process.")

            #5). recover virt-who service 
            self.service_command("restart_virtwho")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
