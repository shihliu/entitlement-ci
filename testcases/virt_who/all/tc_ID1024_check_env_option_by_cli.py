from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1024_check_env_option_by_cli(VIRTWHOBase):
    def run_kvm(self):
        try:
            remote_ip = get_exported_param("REMOTE_IP")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            error_msg_without_env = self.get_vw_cons("libvirt_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("libvirt_error_msg_with_wrong_env")
            libvirt_owner, libvirt_env, libvirt_username, libvirt_password = self.get_libvirt_info()
            self.runcmd_service("stop_virtwho", remote_ip_2)

            # (1) When "--libvirt-env" is not exist, virt-who should show error info
            cmd_without_env = "virt-who --libvirt --libvirt-owner=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password=%s" % (libvirt_owner, remote_ip, libvirt_username, libvirt_password) + " -o -d"
            self.vw_check_message(cmd_without_env, error_msg_without_env, cmd_retcode=1, targetmachine_ip=remote_ip_2)
            # (2) When "--libvirt-env" with wrong config, virt-who should show error info
            cmd_with_wrong_owner = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password=%s" % (libvirt_owner, self.get_vw_cons("wrong_env"), remote_ip, libvirt_username, libvirt_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_owner, error_msg_with_wrong_env, targetmachine_ip=remote_ip_2)
            # (3) When "--libvirt-env" with correct config, virt-who should show error info
            cmd = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password=%s" % (libvirt_owner, libvirt_env, remote_ip, libvirt_username, libvirt_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1, remote_ip_2)
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
            rhevm_version = self.cm_get_rpm_version("rhevm", rhevm_ip)
            if "rhevm-4"in rhevm_version:
                rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443" + "\/ovirt-engine\/"
            else:
                rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443"
            self.runcmd_service("stop_virtwho")

            # (1) When "--rhevm-env" is not exist, virt-who should show error info
            cmd_without_env = "virt-who --rhevm --rhevm-owner=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_server, rhevm_username, rhevm_password) + " -o -d"
            self.vw_check_message(cmd_without_env, error_msg_without_env, cmd_retcode=1)
            # (2) When "--rhevm-env" with wrong config, virt-who should show error info
            cmd_with_wrong_env = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, self.get_vw_cons("wrong_env"), rhevm_server, rhevm_username, rhevm_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_env, error_msg_with_wrong_env)
            # (3) When "--rhevm-env" with correct config, virt-who shouldn't show error info
            cmd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            error_msg_without_env = self.get_vw_cons("hyperv_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("hyperv_error_msg_with_wrong_env")
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            self.runcmd_service("stop_virtwho")

            # (1) When "--hyperv-env" is not exist, virt-who should show error info
            cmd_without_owner = "virt-who --hyperv --hyperv-owner=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % (hyperv_owner, hyperv_server, hyperv_username, hyperv_password) + " -o -d"
            self.vw_check_message(cmd_without_owner, error_msg_without_env, cmd_retcode=1)
            # (2) When "--hyperv-env" with wrong config, virt-who should show error info
            cmd_with_wrong_owner = "virt-who --hyperv --hyperv-owner=%s --hyperv-env=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % (hyperv_owner, self.get_vw_cons("wrong_env"), hyperv_server, hyperv_username, hyperv_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_owner, error_msg_with_wrong_env)
            # (3) When "--hyperv-env" with correct config, virt-who should show error info
            cmd = "virt-who --hyperv --hyperv-owner=%s --hyperv-env=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % (hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            error_msg_without_env = self.get_vw_cons("esx_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("esx_error_msg_with_wrong_env")
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            cmd_without_env = "virt-who --esx --esx-owner=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_message(cmd_without_env, error_msg_without_env, cmd_retcode=1)
            cmd_with_wrong_env = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, self.get_vw_cons("wrong_env"), esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_env, error_msg_with_wrong_env)
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            error_msg_without_env = self.get_vw_cons("xen_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("xen_error_msg_with_wrong_env")
            xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
            self.runcmd_service("stop_virtwho")

            # (1) When "--xen-env" is not exist, virt-who should show error info
            cmd_without_owner = "virt-who --xen --xen-owner=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, xen_server, xen_username, xen_password) + " -o -d"
            self.vw_check_message(cmd_without_owner, error_msg_without_env, cmd_retcode=1)
            # (2) When "--xen-env" with wrong config, virt-who should show error info
            cmd_with_wrong_owner = "virt-who --xen --xen-owner=%s --xen-env=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, self.get_vw_cons("wrong_env"), xen_server, xen_username, xen_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_owner, error_msg_with_wrong_env)
            # (3) When "--xen-env" with correct config, virt-who should show error info
            cmd = "virt-who --xen --xen-owner=%s --xen-env=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, xen_env, xen_server, xen_username, xen_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)
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
