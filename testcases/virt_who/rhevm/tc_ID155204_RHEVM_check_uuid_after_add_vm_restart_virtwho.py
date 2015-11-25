from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID155204_RHEVM_check_uuid_after_add_vm_restart_virtwho(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            rhevm_ip = get_exported_param("RHEVM_IP")
            VIRTWHO_RHEVM_OWNER = self.get_vw_cons("VIRTWHO_RHEVM_OWNER")
            VIRTWHO_RHEVM_ENV = self.get_vw_cons("VIRTWHO_RHEVM_ENV")
            VIRTWHO_RHEVM_SERVER = "https:\/\/" + rhevm_ip + ":443"
            VIRTWHO_RHEVM_USERNAME = self.get_vw_cons("VIRTWHO_RHEVM_USERNAME")
            VIRTWHO_RHEVM_PASSWORD = self.get_vw_cons("VIRTWHO_RHEVM_PASSWORD")
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")

#             (1) Update refresh interval then restart virt-who
            self.update_rhel_rhevm_configure("2", VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV, VIRTWHO_RHEVM_SERVER, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_PASSWORD, debug=1)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=True)
#             (2) stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)
#             check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=False)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.update_rhel_rhevm_configure("5", VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV, VIRTWHO_RHEVM_SERVER, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_PASSWORD, debug=1)
            self.service_command("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
