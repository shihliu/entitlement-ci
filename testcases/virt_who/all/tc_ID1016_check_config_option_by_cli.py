from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1016_check_config_option_by_cli(VIRTWHOBase):
    def run_kvm(self):
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            self.runcmd_service("stop_virtwho", remote_ip_2)
            mode = "libvirt"

#           (1) Check virt-who send h/g mapping info one time when run "virt-who -c "
            conf_file = "/etc/virt-who.d/virt-who.conf"
            self.set_virtwho_sec_config(mode, remote_ip_2)
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1, remote_ip_2)
#           (2) Check virt-who send h/g mapping info one time when run "virt-who -config "
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1, remote_ip_2)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
            remote_ip_1 = get_exported_param("REMOTE_IP_1")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guestuuid = self.vw_get_uuid(guest_name, remote_ip_1)
            mode = "libvirt"

#           (1) Check virt-who send h/g mapping info one time when run "virt-who -c "
            self.runcmd_service("stop_virtwho")
            conf_file = "/etc/virt-who.d/virt-who.conf"
            self.set_virtwho_sec_config(mode)
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
#           (2) Check virt-who send h/g mapping info one time when run "virt-who -config "
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            self.unset_all_virtwho_d_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.runcmd_service("stop_virtwho")

#           (1) Check virt-who send h/g mapping info one time when run "virt-who -c "
            conf_file = "/etc/virt-who.d/virt-who.conf"
            self.set_virtwho_sec_config("rhevm")
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
#           (2) Check virt-who send h/g mapping info one time when run "virt-who -config "
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_RHEVM")

#           (1) Check virt-who send h/g mapping info one time when run "virt-who -c "
            conf_file = "/etc/virt-who.d/virt-who.conf"
            self.set_virtwho_sec_config("rhevm")
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
#           (2) Check virt-who send h/g mapping info one time when run "virt-who -config "
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_HYPERV")

#           (1) Check virt-who send h/g mapping info one time when run "virt-who -c "
            conf_file = "/etc/virt-who.d/virt-who.conf"
            self.set_virtwho_sec_config("hyperv")
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
#           (2) Check virt-who send h/g mapping info one time when run "virt-who -config "
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.runcmd_service("stop_virtwho")
            conf_file, conf_data = self.set_virtwho_d_data("esx")
            self.set_virtwho_d_conf(conf_file, conf_data)
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_XEN")

#           (1) Check virt-who send h/g mapping info one time when run "virt-who -c "
            conf_file = "/etc/virt-who.d/virt-who.conf"
            self.set_virtwho_sec_config("xen")
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
#           (2) Check virt-who send h/g mapping info one time when run "virt-who -config "
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            self.unset_virtwho_d_conf(conf_file)
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
