from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1025_check_env_option_by_config(VIRTWHOBase):
    def run_kvm(self):
        try:
            remote_ip = get_exported_param("REMOTE_IP")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            error_msg_without_env = self.get_vw_cons("libvirt_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("libvirt_error_msg_with_wrong_env")
            libvirt_owner, libvirt_env, libvirt_username, libvirt_password = self.get_libvirt_info()
            self.runcmd_service("stop_virtwho", remote_ip_2)
            self.set_remote_libvirt_conf(remote_ip, remote_ip_2)

            # (1) When "VIRTWHO_LIBVIRT_ENV" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_LIBVIRT_ENV", remote_ip_2)
            if self.get_os_serials(remote_ip_2) == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_env, cmd_retcode=1, targetmachine_ip=remote_ip_2)
            else:
                self.runcmd_service("restart_virtwho", targetmachine_ip=remote_ip_2)
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_env, cmd_retcode=3, targetmachine_ip=remote_ip_2)
            # (2) When "VIRTWHO_LIBVIRT_ENV" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_LIBVIRT_ENV", remote_ip_2)
            self.config_option_setup_value("VIRTWHO_LIBVIRT_ENV", self.get_vw_cons("wrong_env"), remote_ip_2)
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_env, remote_ip_2)
            # (3) When "VIRTWHO_LIBVIRT_ENV" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_LIBVIRT_ENV", libvirt_env, remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(remote_ip_2)
        finally:
            self.update_config_to_default(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            error_msg_without_env = self.get_vw_cons("rhevm_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("rhevm_error_msg_with_wrong_env")
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            rhevm_ip = get_exported_param("RHEVM_IP")
            self.runcmd_service("stop_virtwho")

            # (1) When "VIRTWHO_RHEVM_ENV" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_RHEVM_ENV")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_env, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_env, cmd_retcode=3)
            # (2) When "VIRTWHO_RHEVM_ENV" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_RHEVM_ENV")
            self.config_option_setup_value("VIRTWHO_RHEVM_ENV", self.get_vw_cons("wrong_env"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_env)
            # (3) When "VIRTWHO_RHEVM_ENV" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_RHEVM_ENV", rhevm_env)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.config_option_setup_value("VIRTWHO_RHEVM_ENV", rhevm_env)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            error_msg_without_env = self.get_vw_cons("hyperv_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("hyperv_error_msg_with_wrong_env")
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            self.runcmd_service("stop_virtwho")

            # (1) When "VIRTWHO_HYPERV_ENV" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_HYPERV_ENV")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_env, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_env, cmd_retcode=3)
            # (2) When "VIRTWHO_HYPERV_ENV" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_HYPERV_ENV")
            self.config_option_setup_value("VIRTWHO_HYPERV_ENV", self.get_vw_cons("wrong_env"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_env)
            # (3) When "VIRTWHO_HYPERV_ENV" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_HYPERV_ENV", hyperv_env)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.config_option_setup_value("VIRTWHO_HYPERV_ENV", hyperv_env)
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            error_msg_without_env = self.get_vw_cons("esx_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("esx_error_msg_with_wrong_env")
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_ESX_ENV")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_env, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_env, cmd_retcode=3)
            self.config_option_enable("VIRTWHO_ESX_ENV")
            self.config_option_setup_value("VIRTWHO_ESX_ENV", self.get_vw_cons("wrong_env"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_env)
            self.config_option_setup_value("VIRTWHO_ESX_ENV", esx_env)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.set_esx_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            error_msg_without_env = self.get_vw_cons("xen_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("xen_error_msg_with_wrong_env")
            xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
            self.runcmd_service("stop_virtwho")

            # (1) When "VIRTWHO_XEN_ENV" is not exist, virt-who should show error info
            self.config_option_disable("VIRTWHO_XEN_ENV")
            if self.os_serial == "6":
                self.vw_check_message("service virt-who restart", error_msg_without_env, cmd_retcode=1)
            else:
                self.runcmd_service("restart_virtwho")
                self.vw_check_message("systemctl status virt-who.service", error_msg_without_env, cmd_retcode=3)  # (2) When "VIRTWHO_XEN_ENV" with wrong config, virt-who should show error info
            self.config_option_enable("VIRTWHO_XEN_ENV")
            self.config_option_setup_value("VIRTWHO_XEN_ENV", self.get_vw_cons("wrong_env"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_env)
            # (3) When "VIRTWHO_XEN_ENV" with correct config, virt-who should show error info
            self.config_option_setup_value("VIRTWHO_XEN_ENV", xen_env)
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.config_option_setup_value("VIRTWHO_XEN_ENV", xen_env)
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
