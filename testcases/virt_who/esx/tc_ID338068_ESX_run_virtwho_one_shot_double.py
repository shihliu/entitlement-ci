from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_338068_ESX_run_virtwho_one_shot_double(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:

            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the hostuuid and guestuuid
            host_uuid = self.esx_get_host_uuid(destination_ip)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1). stop virt-who before run oneshot 
            self.service_command("stop_virtwho")

            #2). run virt-who oneshot cmd
            cmd = self.virtwho_cli("esx") + " -o -d "
            ret, output = self.runcmd(cmd, "executing virt-who with one shot")
            if ret == 0 and output is not None and "ERROR" not in output and host_uuid in output and guestuuid in output:
                logger.info("Succeeded to run virt-who with -o -d,  can find uuid from oneshot log message.")
            else:
                raise FailException("Failed to run virt-who with -o -d, can't find uuid from oneshot log meesage.")

            #3). check the status of virt-who, shoud no any virt-who process because the one-shot mode! 
            cmd = "ps -ef | grep -E 'virtwho|virt-who' |grep -v grep"
            ret, output = self.runcmd(cmd, "check the process of virt-who with background mode")
            if ret != 0 and "virtwho.py" not in output and "virt-who.py" not in output:
                logger.info("All the virt-who processes exit successfully!")
            else:
                raise FailException("Failed to stop virt-who process.")

            #4). run virt-who oneshot again
            cmd = self.virtwho_cli("esx") + " -o -d "
            ret, output = self.runcmd(cmd, "executing virt-who with one shot")
            if ret == 0 and output is not None and "ERROR" not in output and host_uuid in output and guestuuid in output:
                logger.info("Succeeded to run virt-who with -o -d,  can find uuid from oneshot log message.")
            else:
                raise FailException("Failed to run virt-who with -o -d, can't find uuid from oneshot log meesage.")

            #5). check the status of virt-who, shoud no any virt-who process because the one-shot mode! 
            cmd = "ps -ef | grep -E 'virtwho|virt-who' |grep -v grep"
            ret, output = self.runcmd(cmd, "check the process of virt-who with background mode")
            if ret != 0 and "virtwho.py" not in output and "virt-who.py" not in output:
                logger.info("All the virt-who processes exit successfully!")
            else:
                raise FailException("Failed to stop virt-who process.")

            #6). recover virt-who service 
            self.service_command("restart_virtwho")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
