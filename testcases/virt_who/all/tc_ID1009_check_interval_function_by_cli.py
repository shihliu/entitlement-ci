from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1009_check_interval_function_by_cli(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.runcmd_service("stop_virtwho")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")
            # (1) Check virt-who refresh default interval is 60s
            cmd = "virt-who -d"
#             self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            self.vw_check_message_number_in_debug_cmd(cmd, check_default_interval, 1, 100)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            cmd = "virt-who -d -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            cmd = "virt-who -d -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 1, 150)
            self.check_virtwho_thread(0)
        finally:
            self.update_vw_configure()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            remote_ip = get_exported_param("REMOTE_IP")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")

            self.runcmd_service("stop_virtwho", remote_ip_2)
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")
            # (1) Check virt-who refresh default interval is 60s
            cmd = self.virtwho_cli("libvirt") + " -d"
#             self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            self.vw_check_message_number_in_debug_cmd(cmd, check_default_interval, 1, 100, targetmachine_ip=remote_ip_2)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            cmd = self.virtwho_cli("libvirt") + " -d -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150, targetmachine_ip=remote_ip_2)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            cmd = self.virtwho_cli("libvirt") + " -d -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 1, 150, targetmachine_ip=remote_ip_2)
            self.check_virtwho_thread(0, remote_ip_2)
        finally:
            self.update_vw_configure(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            self.runcmd_service("stop_virtwho")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            # (1) Check virt-who refresh default interval is 60s
            self.rhevm_start_vm(guest_name, rhevm_ip)
            cmd = "virt-who -d --vdsm"
            self.vw_check_message_number_in_debug_cmd(cmd, check_default_interval, 1, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            cmd = "virt-who -d --vdsm -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            cmd = "virt-who -d --vdsm -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 1, 150)
            self.check_virtwho_thread(0)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.update_rhel_vdsm_configure(5)
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.runcmd_service("stop_virtwho")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            # (1) Check virt-who refresh default interval is 60s
            cmd = self.virtwho_cli("rhevm") + " -d"
            self.vw_check_message_number_in_debug_cmd(cmd, check_default_interval, 1, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            cmd = self.virtwho_cli("rhevm") + " -d -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            cmd = self.virtwho_cli("rhevm") + " -d -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 1, 150)
            self.check_virtwho_thread(0)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            # (1) Check virt-who refresh default interval is 60s
            cmd = self.virtwho_cli("hyperv") + " -d"
#             self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            self.vw_check_message_number_in_debug_cmd(cmd, check_default_interval, 1, 100)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            cmd = self.virtwho_cli("hyperv") + " -d -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            cmd = self.virtwho_cli("hyperv") + " -d -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 1, 150)
            self.check_virtwho_thread(0)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.runcmd_service("stop_virtwho")
            loop_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")
            cmd = self.virtwho_cli("esx") + " -d"
#             self.vw_check_message_number_in_debug_cmd(cmd, loop_msg, 2, 150)
            self.vw_check_message_number_in_debug_cmd(cmd, check_default_interval, 1, 100)
            cmd = self.virtwho_cli("esx") + " -d -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, loop_msg, 2, 150)
            cmd = self.virtwho_cli("esx") + " -d -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, loop_msg, 1, 150)
            self.check_virtwho_thread(0)
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.runcmd_service("stop_virtwho")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            # (1) Check virt-who refresh default interval is 60s
            cmd = self.virtwho_cli("xen") + " -d"
            self.vw_check_message_number_in_debug_cmd(cmd, check_default_interval, 1, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            cmd = self.virtwho_cli("xen") + " -d -i 10"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            cmd = self.virtwho_cli("xen") + " -d -i 120"
            self.vw_check_message_number_in_debug_cmd(cmd, check_msg, 1, 150)
            self.check_virtwho_thread(0)
        finally:
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
