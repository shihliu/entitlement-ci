from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1010_check_interval_function_by_config(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            # (1) Check virt-who refresh default interval is 60s
            self.vw_check_message_number_in_rhsm_log(check_default_interval, 1, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(check_msg, 1, 150)
            # (4).Check virt-who thread will not increase after restart it.
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                self.check_virtwho_thread(1)
                time.sleep(5)
        finally:
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
            remote_ip_1 = get_exported_param("REMOTE_IP_1")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guestuuid = self.vw_get_uuid(guest_name, remote_ip_1)

            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            # (1) Check virt-who refresh default interval is 60s
            self.vw_check_message_number_in_rhsm_log(check_default_interval, 1, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(check_msg, 1, 150)
            # (4).Check virt-who thread will not increase after restart it.
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                if self.virtwho_version[9:13] > 0.20:
                    self.check_virtwho_thread(2)
                else:
                    self.check_virtwho_thread(1)
                time.sleep(5)
        finally:
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")


            # (1) Check virt-who refresh default interval is 60s
            self.rhevm_start_vm(guest_name, rhevm_ip)
            self.vw_check_message_number_in_rhsm_log(check_default_interval, 1, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(check_msg, 1, 150)
            # (4).Check virt-who thread will not increase after restart it.
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                self.check_virtwho_thread(1)
                time.sleep(5)
        finally:
            self.update_rhel_vdsm_configure(5)
            self.runcmd_service("restart_virtwho")
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            # (1) Check virt-who refresh default interval is 60s
            self.vw_check_message_number_in_rhsm_log(check_default_interval, 1, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(check_msg, 1, 150)
            # (4).Check virt-who thread will not increase after restart it.
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                self.check_virtwho_thread(1)
                time.sleep(5)
        finally:
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            # (1) Check virt-who refresh default interval is 3600s
            self.vw_check_message_number_in_rhsm_log(check_default_interval, 1, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(check_msg, 1, 150)
            # (4).Check virt-who thread will not increase after restart it.
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                self.check_virtwho_thread(1)
                time.sleep(5)
        finally:
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            loop_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            self.config_option_disable("VIRTWHO_INTERVAL")
            self.vw_check_message_number_in_rhsm_log(check_default_interval, 1, 150)
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(loop_msg, 2, 150)
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(loop_msg, 1, 150)
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                self.check_virtwho_thread(1)
                time.sleep(5)
        finally:
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            # (1) Check virt-who refresh default interval is 60s
            self.vw_check_message_number_in_rhsm_log(check_default_interval, 1, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(check_msg, 1, 150)
            # (4).Check virt-who thread will not increase after restart it.
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                self.check_virtwho_thread(1)
                time.sleep(5)
        finally:
            self.config_option_disable("VIRTWHO_INTERVAL")
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
