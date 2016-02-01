from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17216_RHEVM_check_env_option_by_cli(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443"
            error_msg = "Option --rhevm-env (or VIRTWHO_RHEVM_ENV environment variable) needs to be set"
            self.runcmd_service("stop_virtwho")
            #(1) When "--rhevm-env" is not exist, virt-who should show error info
            cmd_without_owner = "virt-who --rhevm --rhevm-owner=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_server, rhevm_username, rhevm_password) + " -o -d"
            self.vw_check_message(cmd_without_owner, error_msg, cmd_retcode=1)
            #(2) When "--rhevm-env" with wrong config, virt-who should show error info
            cmd_with_wrong_owner = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, "xxxxxxx", rhevm_server, rhevm_username, rhevm_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_owner, error_msg, cmd_retcode=1)
            #(3) When "--rhevm-env" with correct config, virt-who should show error info
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
