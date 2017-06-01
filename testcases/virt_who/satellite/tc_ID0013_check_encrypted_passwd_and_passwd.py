from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID0013_check_encrypted_passwd_and_passwd(VIRTWHOBase):
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
            error_msg_with_wrong_passwd = self.get_vw_cons("error_msg_with_wrong_passwd")
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            self.runcmd_service("stop_virtwho")
            rhevm_ip = get_exported_param("RHEVM_IP")
            rhevm_version = self.cm_get_rpm_version("rhevm", rhevm_ip)
            if "rhevm-4"in rhevm_version:
                rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443" + "\/ovirt-engine\/"
            else:
                rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443"
            self.runcmd_service("stop_virtwho")
            # (1) Check encrypted_password option in /etc/virt-who.d/xxx
            # (1.1) Disable rhevm mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_RHEVM")
            # (1.2) Check encrypted_password before run virt-who-password cmd
            self.set_encrypted_password("rhevm", "xxxxxxWelcome@*&$001xxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (1.3) Config correct encryped password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(rhevm_password)
            self.set_encrypted_password("rhevm", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (1.4) Config wrong encryped password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("rhevm", "xxxxxxWelcome@*&$001xxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (2) Check password option in /etc/virt-who.d/xxx
            # (2.1) Config correct password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            self.unset_all_virtwho_d_conf()
            self.set_virtwho_sec_config("rhevm")
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2.2) Config wrong password of rhevm mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_virtwho_sec_config_with_keyvalue("rhevm", "password", self.get_vw_cons("wrong_passwd"))
            self.vw_check_timeout_in_rhsm_log(error_msg_with_wrong_passwd)
            # (3) Check rhevm-password option in CLI
            self.unset_all_virtwho_d_conf()
            self.runcmd_service("stop_virtwho")
            # (3.1) Config wrong password of rhevm mode in CLI mode
            cmd_with_wrong_passwd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_env, rhevm_server, rhevm_username, self.get_vw_cons("wrong_passwd")) + " -o -d"
            self.vw_check_message(cmd_with_wrong_passwd, error_msg_with_wrong_passwd)
            # (3.2) When "--rhevm-passwd" with correct config, virt-who send mapping info
            cmd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            error_msg_with_wrong_passwd = self.get_vw_cons("error_msg_with_wrong_passwd")
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            self.runcmd_service("stop_virtwho")
            # (1) Check encrypted_password option in /etc/virt-who.d/xxx
            # (1.1) Disable hyperv mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_HYPERV")
            # (1.2) Check encrypted_password before run virt-who-password cmd
            self.set_encrypted_password("hyperv", "xxxxxxWelcome@*&$001xxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (1.3) Config correct encryped password of hyperv mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(hyperv_password)
            self.set_encrypted_password("hyperv", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (1.4) Config wrong encryped password of hyperv mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("hyperv", "xxxxxxWelcome@*&$001xxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (2) Check password option in /etc/virt-who.d/xxx
            # (2.1) Config correct password of hyperv mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            self.unset_all_virtwho_d_conf()
            self.set_virtwho_sec_config("hyperv")
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2.2) Config wrong password of hyperv mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_virtwho_sec_config_with_keyvalue("hyperv", "password", self.get_vw_cons("wrong_passwd"))
            self.vw_check_timeout_in_rhsm_log(error_msg_with_wrong_passwd)
            # (3) Check hyperv-password option in CLI
            self.unset_all_virtwho_d_conf()
            self.runcmd_service("stop_virtwho")
            # (3.1) Config wrong password of hyperv mode in CLI mode
            cmd_with_wrong_passwd = "virt-who --hyperv --hyperv-owner=%s --hyperv-env=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % (hyperv_owner, hyperv_env, hyperv_server, hyperv_username, self.get_vw_cons("wrong_passwd")) + " -o -d"
            self.vw_check_message(cmd_with_wrong_passwd, error_msg_with_wrong_passwd)
            # (3.2) When "--hyperv-passwd" with correct config, virt-who send mapping info
            cmd = "virt-who --hyperv --hyperv-owner=%s --hyperv-env=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % (hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            error_msg_with_wrong_passwd = self.get_vw_cons("error_msg_with_wrong_passwd")
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            # (1) Check encrypted_password option in /etc/virt-who.d/xxx
            # (1.1) Disable esx mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_ESX")
            # (1.2) Check encrypted_password before run virt-who-password cmd
            self.set_encrypted_password("esx", "xxxxxxWelcome@*&$001xxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (1.3) Config correct encryped password of esx mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(esx_password)
            self.set_encrypted_password("esx", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (1.4) Config wrong encryped password of esx mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("esx", "xxxxxxWelcome@*&$001xxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (2) Check password option in /etc/virt-who.d/xxx
            # (2.1) Config correct password of esx mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            self.unset_all_virtwho_d_conf()
            self.set_virtwho_sec_config("esx")
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2.2) Config wrong password of esx mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_virtwho_sec_config_with_keyvalue("esx", "password", self.get_vw_cons("wrong_passwd"))
            self.vw_check_timeout_in_rhsm_log(error_msg_with_wrong_passwd)
            # (3) Check esx-password option in CLI
            self.unset_all_virtwho_d_conf()
            self.runcmd_service("stop_virtwho")
            # (3.1) Config wrong password of esx mode in CLI mode
            cmd_with_wrong_passwd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, self.get_vw_cons("wrong_passwd")) + " -o -d"
            self.vw_check_message(cmd_with_wrong_passwd, error_msg_with_wrong_passwd)
            # (3.2) When "--esx-passwd" with correct config, virt-who send mapping info
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            error_msg_with_wrong_passwd = self.get_vw_cons("error_msg_with_wrong_passwd")
            xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
            self.runcmd_service("stop_virtwho")
            # (1) Check encrypted_password option in /etc/virt-who.d/xxx
            # (1.1) Disable xen mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_XEN")
            # (1.2) Check encrypted_password before run virt-who-password cmd
            self.set_encrypted_password("xen", "xxxxxxWelcome@*&$001xxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (1.3) Config correct encryped password of xen mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(xen_password)
            self.set_encrypted_password("xen", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (1.4) Config wrong encryped password of xen mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("xen", "xxxxxxWelcome@*&$001xxxx")
            self.vw_check_message_in_rhsm_log("can't be decrypted, possibly corrupted")
            # (2) Check password option in /etc/virt-who.d/xxx
            # (2.1) Config correct password of xen mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            self.unset_all_virtwho_d_conf()
            self.set_virtwho_sec_config("xen")
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (2.2) Config wrong password of xen mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_virtwho_sec_config_with_keyvalue("xen", "password", self.get_vw_cons("wrong_passwd"))
            self.vw_check_timeout_in_rhsm_log(error_msg_with_wrong_passwd)
            # (3) Check xen-password option in CLI
            self.unset_all_virtwho_d_conf()
            self.runcmd_service("stop_virtwho")
            # (3.1) Config wrong password of xen mode in CLI mode
            cmd_with_wrong_passwd = "virt-who --xen --xen-owner=%s --xen-env=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, xen_env, xen_server, xen_username, self.get_vw_cons("wrong_passwd")) + " -o -d"
            self.vw_check_message(cmd_with_wrong_passwd, error_msg_with_wrong_passwd)
            # (3.2) When "--xen-passwd" with correct config, virt-who send mapping info
            cmd = "virt-who --xen --xen-owner=%s --xen-env=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, xen_env, xen_server, xen_username, xen_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)
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