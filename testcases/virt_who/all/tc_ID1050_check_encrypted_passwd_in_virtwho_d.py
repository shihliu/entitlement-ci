from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1050_check_encrypted_passwd_in_virtwho_d(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.skipTest("test case skiped, not fit for kvm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            self.runcmd_service("stop_virtwho")

            # (1) Disable rhevm mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_RHEVM")
            # (2) Config correct encryped password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(rhevm_password)
            self.set_encrypted_password("rhevm", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (3) Config wrong encryped password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("rhevm", "xxxxxxxxxxxxxxxxxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            self.runcmd_service("stop_virtwho")

            # (1) Disable hyperv mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_HYPERV")
            # (2) Config correct encryped password of hyperv mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(hyperv_password)
            self.set_encrypted_password("hyperv", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (3) Config wrong encryped password of hyperv mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("hyperv", "xxxxxxxxxxxxxxxxxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            self.unset_esx_conf()
            encrypted_password = self.run_virt_who_password(esx_password)
            self.set_encrypted_password("esx", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            self.set_encrypted_password("esx", "xxxxxxxxxxxxxxxxxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
            self.runcmd_service("stop_virtwho")

            # (1) Disable xen mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_XEN")
            # (2) Config correct encryped password of xen mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(xen_password)
            self.set_encrypted_password("xen", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (3) Config wrong encryped password of xen mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("xen", "xxxxxxxxxxxxxxxxxxx")
            self.vw_check_message_in_rhsm_log(self.get_vw_cons("xen_error_msg_wrong_encryped_password"))
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
