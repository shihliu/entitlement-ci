from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1022_check_owner_option_by_config(VIRTWHOBase):
    def run_kvm(self):
        try:
            remote_ip = get_exported_param("REMOTE_IP")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            error_msg_without_owner = self.get_vw_cons("libvirt_error_msg_without_owner")
            error_msg_with_wrong_owner = self.get_vw_cons("libvirt_error_msg_with_wrong_owner")
            libvirt_owner, libvirt_env, libvirt_username, libvirt_password = self.get_libvirt_info()
            self.runcmd_service("stop_virtwho", remote_ip_2)
            self.set_remote_libvirt_conf(remote_ip, remote_ip_2)

            # (1) When "VIRTWHO_LIBVIRT_OWNER" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_LIBVIRT_OWNER", remote_ip_2)
            if self.get_os_serials(remote_ip_2) == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_owner, cmd_retcode=1, targetmachine_ip=remote_ip_2)
            else:
                self.runcmd_service("restart_virtwho", targetmachine_ip=remote_ip_2)
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_owner, cmd_retcode=3, targetmachine_ip=remote_ip_2)
            # (2) When "VIRTWHO_LIBVIRT_OWNER" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_LIBVIRT_OWNER", remote_ip_2)
            self.config_option_setup_value("VIRTWHO_LIBVIRT_OWNER", self.get_vw_cons("wrong_owner"), remote_ip_2)
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_owner, targetmachine_ip=remote_ip_2)
            # (3) When "VIRTWHO_LIBVIRT_OWNER" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_LIBVIRT_OWNER", libvirt_owner, remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(targetmachine_ip=remote_ip_2)
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            error_msg_without_owner = self.get_vw_cons("rhevm_error_msg_without_owner")
            error_msg_with_wrong_owner = self.get_vw_cons("rhevm_error_msg_with_wrong_owner")
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            rhevm_ip = get_exported_param("RHEVM_IP")
            self.runcmd_service("stop_virtwho")

            # (1) When "VIRTWHO_RHEVM_OWNER" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_RHEVM_OWNER")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_owner, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("service virt-who status", error_msg_without_owner, cmd_retcode=3)  
            # (2) When "VIRTWHO_RHEVM_OWNER" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_RHEVM_OWNER")
            self.config_option_setup_value("VIRTWHO_RHEVM_OWNER", self.get_vw_cons("wrong_owner"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_owner)
            # (3) When "VIRTWHO_RHEVM_OWNER" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_RHEVM_OWNER", rhevm_owner)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.config_option_setup_value("VIRTWHO_RHEVM_OWNER", rhevm_owner)
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            error_msg_without_owner = self.get_vw_cons("hyperv_error_msg_without_owner")
            error_msg_with_wrong_owner = self.get_vw_cons("hyperv_error_msg_with_wrong_owner")
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            self.runcmd_service("stop_virtwho")

            # (1) When "VIRTWHO_HYPERV_OWNER" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_HYPERV_OWNER")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_owner, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_owner, cmd_retcode=3)
            # (2) When "VIRTWHO_HYPERV_OWNER" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_HYPERV_OWNER")
            self.config_option_setup_value("VIRTWHO_HYPERV_OWNER", self.get_vw_cons("wrong_owner"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_owner)
            # (3) When "VIRTWHO_HYPERV_OWNER" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_HYPERV_OWNER", hyperv_owner)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            error_msg_without_owner = self.get_vw_cons("esx_error_msg_without_owner")
            error_msg_with_wrong_owner = self.get_vw_cons("esx_error_msg_with_wrong_owner")
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_ESX_OWNER")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_owner, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_owner, cmd_retcode=3)
            self.config_option_enable("VIRTWHO_ESX_OWNER")
            self.config_option_setup_value("VIRTWHO_ESX_OWNER", self.get_vw_cons("wrong_owner"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_owner)
            self.config_option_setup_value("VIRTWHO_ESX_OWNER", esx_owner)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.set_esx_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            error_msg_without_owner = self.get_vw_cons("xen_error_msg_without_owner")
            error_msg_with_wrong_owner = self.get_vw_cons("xen_error_msg_with_wrong_owner")
            xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
            self.runcmd_service("stop_virtwho")

            # (1) When "VIRTWHO_XEN_OWNER" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_XEN_OWNER")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_owner, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_owner, cmd_retcode=3)  # (2) When "VIRTWHO_XEN_OWNER" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_XEN_OWNER")
            self.config_option_setup_value("VIRTWHO_XEN_OWNER", self.get_vw_cons("wrong_owner"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_owner)
            # (3) When "VIRTWHO_XEN_OWNER" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_XEN_OWNER", xen_owner)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.set_xen_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            hypervisor_type = get_exported_param("HYPERVISOR_TYPE")
            if hasattr(self, "run_" + hypervisor_type):
                getattr(self, "run_" + hypervisor_type)()
            else:
                self.skipTest("test case skiped, not fit for %s" % hypervisor_type)
            self.assert_(True, case_name)
        except Exception, SkipTest:
            logger.info(str(SkipTest))
            raise SkipTest
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
