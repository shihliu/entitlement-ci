from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1005_check_debug_function_by_cli(VIRTWHOBase):
    def run_kvm(self):
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            # (1) Run virt-who, check debug info is not exist on virt-who log.
            self.runcmd_service("stop_virtwho")
            self.vw_check_message_in_debug_cmd("virt-who", "DEBUG|ERROR", message_exists=False)
            # (2) Run virt-who -d, check guest uuid and DEBUG exist on virt-who log.
            self.vw_check_message_in_debug_cmd("virt-who -d", "%s|using libvirt as backend|DEBUG" % guestuuid, message_exists=True)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            # (1) Run virt-who, check debug info is not exist on virt-who log.
            self.runcmd_service("stop_virtwho")
            self.vw_check_message_in_debug_cmd("virt-who", "DEBUG|ERROR|%s" % guestuuid, message_exists=False)
            # (2) Run virt-who -d, check guest uuid and DEBUG exist on virt-who log.
            self.rhevm_start_vm(guest_name, rhevm_ip)
            self.runcmd_service("stop_virtwho")
            self.vw_check_message_in_debug_cmd("virt-who --vdsm -d", "%s|\"vdsm\" mode|DEBUG" % guestuuid, message_exists=True)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Check "DEBUG" info is exist when run "virt-who --rhevm -d"
            cmd = self.virtwho_cli("rhevm") + " -d"
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG")
            # (2) Check "DEBUG" info is not exist when run "virt-who --rhevm",no "-d" option
            cmd = self.virtwho_cli("rhevm")
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG|ERROR", message_exists=False)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Check "DEBUG" info is exist when run "virt-who --hyperv -d"
            cmd = self.virtwho_cli("hyperv") + " -d"
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG")
            # (2) Check "DEBUG" info is not exist when run "virt-who --hyperv",no "-d" option
            cmd = self.virtwho_cli("hyperv")
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG|ERROR", message_exists=False)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.runcmd_service("stop_virtwho")
            cmd = self.virtwho_cli("esx") + " -d"
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG")
            cmd = self.virtwho_cli("esx")
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG", message_exists=False)
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Check "DEBUG" info is exist when run "virt-who --xen -d"
            cmd = self.virtwho_cli("xen") + " -d"
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG")
            # (2) Check "DEBUG" info is not exist when run "virt-who --xen",no "-d" option
            cmd = self.virtwho_cli("xen")
            self.vw_check_message_in_debug_cmd(cmd, "DEBUG|ERROR", message_exists=False)
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
