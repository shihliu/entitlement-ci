from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17216_RHEVM_check_env_option_by_cli(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
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
            # (3) When "--rhevm-env" with correct config, virt-who should show error info
            cmd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
