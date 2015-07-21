from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID202506_ESX_execute_virtwho_b(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_owner = VIRTWHOConstants().get_constant("VIRTWHO_ESX_OWNER")
            esx_env = VIRTWHOConstants().get_constant("VIRTWHO_ESX_ENV")
            esx_server = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
            esx_username = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
            esx_password = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")
            
            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")

            #1). stop virt-who service
            self.vw_stop_virtwho_new()

            #2). Execute virt-who in the background mode.
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -b -d" %(esx_owner,esx_env,esx_server,esx_username,esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with -b -d")
            if ret == 0:
                logger.info("Succeeded to execute virt-who with -b -d ")
            else:
                raise FailException("Failed to execute virt-who with -b -d")

            #3). check the status of virt-who
            cmd = "ps -ef | grep -E 'virtwho|virt-who'"
            ret, output = self.runcmd(cmd, "check the process of virt-who with background mode")
            if ret == 0 and (("virtwho.py" in output) or ("virt-who.py" in output)):
                logger.info("Succeeded to check virt-who process.")
            else:
                raise FailException("Failed to check virt-who process.")

            # (1) start a guest    
            self.esx_start_guest(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip)
            # (2)pause a guest
            self.esx_pause_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip)
            # (3)resume a guest
            self.esx_resume_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip)
            # (4)shutdown a guest
            self.esx_stop_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip)
            # (5)delete a guest
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)
            # prepare test env: undefine the guest to handle
            self.esx_remove_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip, guestuuid, uuidexists=False)
            # (6)add a guest.
            self.esx_add_guest(guest_name, destination_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.esx_check_uuid(guest_name, destination_ip)
            self.vw_stop_virtwho_new()

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
