from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1006_check_debug_function_by_config(VIRTWHOBase):
    def run_kvm(self):
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) enable debug mode, check debug info is exist on virt-who log.
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.vw_check_message_in_rhsm_log("%s|using libvirt as backend|DEBUG" % guestuuid, message_exists=True)

            # (2) diable debug mode, check debug info is not exist on virt-who log.
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            self.vw_check_message_in_rhsm_log("DEBUG|ERROR", message_exists=False)
            self.vw_check_message_in_rhsm_log("guests found")
        finally:
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # (1) enable debug mode, check debug info is exist on virt-who log.
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            self.runcmd_service("stop_virtwho")
            self.vw_check_message_in_debug_cmd("virt-who --vdsm -d", "%s|\"vdsm\" mode|DEBUG" % guestuuid, message_exists=True)

            # (2) diable debug mode, check debug info is not exist on virt-who log.
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            self.vw_check_message_in_rhsm_log("DEBUG|ERROR", message_exists=False)
            self.vw_check_message_in_rhsm_log("guests found")
        finally:
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Check "DEBUG" info is exist when run enable "VIRTWHO_DEBUG" in /etc/sysconfig/virt-who
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.vw_check_message_in_rhsm_log("DEBUG")
            self.runcmd_service("stop_virtwho")
            # (2) Check "DEBUG" info is not exist when run disable "VIRTWHO_DEBUG" in /etc/sysconfig/virt-who
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            self.vw_check_message_in_rhsm_log("DEBUG", message_exists=False)
            self.vw_check_message_in_rhsm_log("hypervisors and|guests found")
        finally:
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Check "DEBUG" info is exist when run enable "VIRTWHO_DEBUG" in /etc/sysconfig/virt-who
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.vw_check_message_in_rhsm_log("DEBUG")
            self.runcmd_service("stop_virtwho")
            # (2) Check "DEBUG" info is not exist when run disable "VIRTWHO_DEBUG" in /etc/sysconfig/virt-who
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            self.vw_check_message_in_rhsm_log("DEBUG", message_exists=False)
            self.vw_check_message_in_rhsm_log("hypervisors and|guests found")
        finally:
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.vw_check_message_in_rhsm_log("DEBUG")
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            self.vw_check_message_in_rhsm_log("DEBUG", message_exists=False)
            self.vw_check_message_in_rhsm_log("hypervisors and|guests found")
        finally:
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Check "DEBUG" info is exist when run enable "VIRTWHO_DEBUG" in /etc/sysconfig/virt-who
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.vw_check_message_in_rhsm_log("DEBUG")
            self.runcmd_service("stop_virtwho")
            # (2) Check "DEBUG" info is not exist when run disable "VIRTWHO_DEBUG" in /etc/sysconfig/virt-who
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            self.vw_check_message_in_rhsm_log("DEBUG", message_exists=False)
            self.vw_check_message_in_rhsm_log("hypervisors and|guests found")
        finally:
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
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
