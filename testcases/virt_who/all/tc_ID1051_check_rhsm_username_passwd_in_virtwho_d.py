from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1051_check_rhsm_username_passwd_in_virtwho_d(VIRTWHOBase):
    def run_kvm(self):
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            self.update_config_to_default(remote_ip_2)
            self.update_vw_configure(targetmachine_ip=remote_ip_2)
            self.runcmd_service("stop_virtwho", remote_ip_2)

            # (1) Config libvirt mode in /etc/virt-who.d with correct rhsm_username and rhsm_password
            self.set_rhsm_user_pass("libvirt", server_user, server_pass, remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(targetmachine_ip=remote_ip_2)
            # (2) Config libvirt mode in /etc/virt-who.d with wrong rhsm_username and rhsm_password
            self.set_rhsm_user_pass("libvirt", server_user, "xxxxxxxx", remote_ip_2)
            self.vw_check_message_in_rhsm_log("Invalid username or password", targetmachine_ip=remote_ip_2)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            self.runcmd_service("stop_virtwho")

            # (1) Disable rhevm mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_RHEVM")
            # (2) Config rhevm mode in /etc/virt-who.d with correct rhsm_username and rhsm_password
            self.set_rhsm_user_pass("rhevm", server_user, server_pass)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (3) Config rhevm mode in /etc/virt-who.d with wrong rhsm_username and rhsm_password
            self.set_rhsm_user_pass("rhevm", server_user, "xxxxxxxx")
            self.vw_check_message_in_rhsm_log("BUG yet|Invalid username or password")
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            self.runcmd_service("stop_virtwho")

            # (1) Disable hyperv mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_HYPERV")
            # (2) Config hyperv mode in /etc/virt-who.d with correct rhsm_username and rhsm_password
            self.set_rhsm_user_pass("hyperv", server_user, server_pass)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (3) Config hyperv mode in /etc/virt-who.d with wrong rhsm_username and rhsm_password
            self.set_rhsm_user_pass("hyperv", server_user, "xxxxxxxx")
            self.vw_check_message_in_rhsm_log("Invalid username or password")
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            self.runcmd_service("stop_virtwho")
            self.unset_esx_conf()
            self.set_rhsm_user_pass("esx", server_user, server_pass)
            self.vw_check_mapping_info_number_in_rhsm_log()
            self.set_rhsm_user_pass("esx", server_user, "xxxxxxxx")
            self.vw_check_message_in_rhsm_log("BUG yet|Invalid username or password")
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            self.runcmd_service("stop_virtwho")

            # (1) Disable xen mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_XEN")
            # (2) Config xen mode in /etc/virt-who.d with correct rhsm_username and rhsm_password
            self.set_rhsm_user_pass("xen", server_user, server_pass)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (3) Config xen mode in /etc/virt-who.d with wrong rhsm_username and rhsm_password
            self.set_rhsm_user_pass("xen", server_user, "xxxxxxxx")
            self.vw_check_message_in_rhsm_log("BUG yet|Invalid username or password")
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_xen_conf()
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
