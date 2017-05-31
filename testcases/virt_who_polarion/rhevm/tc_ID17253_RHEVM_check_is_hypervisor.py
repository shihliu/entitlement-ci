from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17253_RHEVM_check_is_hypervisor(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_RHEVM")

            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_uuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # (1) Set rhevm fake mode with is_hypervisor=True, it will not show host/guest mapping info
            self.runcmd_service("stop_virtwho")
            fake_file = self.generate_fake_file("rhevm")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set rhevm fake mode, stop guest, it still show host/guest mapping info
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Set rhevm fake mode with is_hypervisor=False, it will not show host/guest mapping info
            self.runcmd_service("stop_virtwho")
            fake_file = self.generate_fake_file("rhevm")
            self.set_fake_mode_conf(fake_file, "False", virtwho_owner, virtwho_env)
            self.vw_check_message_in_rhsm_log(host_uuid, message_exists=False)
            # (3) Set hyperv fake mode with is_hypervisor=False, it will remind is_hypevisor is not correct
            chkmsg = "uuid key shouldn't be present, try to check is_hypervisor value"
            self.vw_check_message_in_rhsm_log(("%s|is not properly formed" % chkmsg), message_exists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
