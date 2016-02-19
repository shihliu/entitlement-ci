from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17253_HYPERV_check_is_hypervisor(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_HYPERV")

            virtwho_owner = self.get_vw_cons("VIRTWHO_HYPERV_OWNER")
            virtwho_env = self.get_vw_cons("VIRTWHO_HYPERV_ENV")
            guest_name = self.get_vw_cons("HYPERV_GUEST_NAME")
            hyperv_host_ip = self.get_vw_cons("HYPERV_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()
            
            # (1) Set hyperv fake mode with is_hypervisor=True, it will show host/guest mapping info
            fake_file = self.generate_fake_file("hyperv")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set hyperv fake mode with is_hypervisor=False, it will not show host/guest mapping info
            self.runcmd_service("stop_virtwho")
            fake_file = self.generate_fake_file("hyperv")
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
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
