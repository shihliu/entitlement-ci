from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID443912_ESX_run_virtwho_with_wrong_encrypted_password(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:

            VIRTWHO_ESX_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_OWNER")
            VIRTWHO_ESX_ENV = VIRTWHOConstants().get_constant("VIRTWHO_ESX_ENV")
            VIRTWHO_ESX_SERVER = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
            VIRTWHO_ESX_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
            VIRTWHO_ESX_PASSWORD = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the guest is power off or not on esxi host, if power on, stop it firstly 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1). stop virt-who firstly 
            self.service_command("stop_virtwho")

            #2). disable esx config
            self.unset_esx_conf()

            #3). input an error decrypt encrypted password for testing
            encrypted_password = "xxxxxxxx"

            #4). creat /etc/virt-who.d/virt.esx file for esxi
            conf_file = "/etc/virt-who.d/virt.esx"
            conf_data = '''[test-esx1]
type=esx
server=%s
username=%s
encrypted_password=%s
owner=%s
env=%s''' % (VIRTWHO_ESX_SERVER, VIRTWHO_ESX_USERNAME, encrypted_password, VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV)

            if self.set_virtwho_d_conf(conf_file, conf_data):
                raise FailException("Failed, virt-who shouldn't restart with an error encrypted_password.")
            else:
                logger.info("Succeeded, virt-who is not restarted with an error encrypted_password.")

            #5). virt-who restart
            print self.service_command("restart_virtwho", is_return=True)

            #6). check whether the host/guest association info has been sent to server
            if self.esx_check_uuid_exist_in_rhsm_log(host_uuid) or self.esx_check_uuid_exist_in_rhsm_log(guestuuid):
                raise FailException("Failed to check uuid list, should be no uuid list found with an error encrypted_password.")
            else:
                logger.info("Succeeded to check uuid list, no uuid list found with an error encrypted_password.")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            self.set_esx_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

