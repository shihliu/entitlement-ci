from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID0007_check_sec_config_file(VIRTWHOBase):
    def run_kvm(self):
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            self.runcmd_service("stop_virtwho", remote_ip_2)
            self.update_vw_configure(targetmachine_ip=remote_ip_2)
            # (1) on host2, run commond line mode to monitor remote libvirt
            self.set_virtwho_sec_config("libvirt", remote_ip_2)
            self.vw_check_mapping_info_number_in_rhsm_log(targetmachine_ip=remote_ip_2)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.runcmd_service("stop_virtwho")
            for i in range(1, 5):
                self.vw_check_mapping_info_number("virt-who --vdsm -o -d", 1)
            self.check_virtwho_thread(0)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Disable rhevm mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_RHEVM")
            # (2) Config rhevm mode in /etc/virt-who.d
            self.set_virtwho_sec_config("rhevm")
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.set_rhevm_conf()
            self.unset_all_virtwho_d_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Disable hyperv mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_HYPERV")
            # (2) Config hyperv mode in /etc/virt-who.d
            self.set_virtwho_sec_config("hyperv")
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.set_hyperv_conf()
            self.unset_all_virtwho_d_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Disable esx mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_ESX")
            # (2) Config esx mode in /etc/virt-who.d
            self.set_virtwho_sec_config("esx")
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.set_esx_conf()
            self.unset_all_virtwho_d_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Disable xen mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_XEN")
            # (2) Config xen mode in /etc/virt-who.d
            self.set_virtwho_sec_config("xen")
            self.vw_check_mapping_info_number_in_rhsm_log()
        finally:
            self.set_xen_conf()
            self.unset_all_virtwho_d_conf()
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