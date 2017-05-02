from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1004_check_default_config(VIRTWHOBase):
    def run_kvm(self):
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            self.vw_start_guests(guest_name)
            # (1) Set virt-who config to default.
            self.update_config_to_default()
            # (2) Check if debug info is not show on virt-who log.
            self.vw_check_message_in_rhsm_log("Sending update in guests lists", message_exists=True)
            # (3) Check debug info is not exist on virt-who log.
            self.vw_check_message_in_rhsm_log("DEBUG", message_exists=False)
            # (4) Check virt-who processes and virt-who service status.
            self.check_virtwho_thread(2)
            self.vw_check_virtwho_status()
            # (5) Stop virt-who service and check virt-who processes.
            self.vw_stop_virtwho()
            self.check_virtwho_thread(0)
            # (6) Run virt-who commond line, check debug info is not exist in virt-who log.
            self.vw_check_message_in_debug_cmd("virt-who", "DEBUG|ERROR", message_exists=False)
            # (7) Run virt-who commond line, check guest uuid exist on virt-who log.
            self.vw_check_message_in_debug_cmd("virt-who", "Sending update in guests lists for config|using libvirt as backend", message_exists=True)
            # (8) Press Ctrl+C to kill virt-who
            self.runcmd_ctrl_c("virt-who", "run virt-who command and kill with Ctrl+C")
            self.check_virtwho_thread(0)
        finally:
            self.vw_stop_guests(guest_name)
            self.update_vw_configure()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.skipTest("test case skiped, not fit for rhevm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.skipTest("test case skiped, not fit for hyperv ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.skipTest("test case skiped, not fit for esx ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.skipTest("test case skiped, not fit for xen ...")
        finally:
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
