from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID174959_ESX_validate_mapping_info_after_re_register_host(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SAM_IP")
            SAM_HOSTNAME = get_exported_param("SAM_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")

            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the guest is power off or not on esxi host, if power on, stop it 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1). register esxi host on sam by restart virt-who service 
            self.vw_restart_virtwho_new() 

            #2). check esxi host is registered or not on sam
            time.sleep(10)
            self.esx_check_host_in_samserv(host_uuid, SAM_IP)

            #3). unregister or remove esxi host from sam 
            self.vw_stop_virtwho_new()
            self.esx_remove_host_in_samserv(host_uuid, SAM_IP)
            #self.esx_remove_deletion_record_in_samserv(host_uuid, SAM_IP)

            #4). re-register esxi host on sam by restart virt-who service 
            self.vw_restart_virtwho_new() 

            #5). check esxi host is registered or not on sam again, and check guest uuid from rhsm.log
            time.sleep(20)
            self.esx_check_host_in_samserv(host_uuid, SAM_IP)

            #6). check host/guest association from rhsm.log
            self.esx_check_uuid_exist_in_rhsm_log(host_uuid)
            self.esx_check_uuid_exist_in_rhsm_log(guestuuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)

        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # Unregister the ESX host 
            self.esx_unsubscribe_all_host_in_samserv(host_uuid, SAM_IP)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
