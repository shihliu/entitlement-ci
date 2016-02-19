from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17213_HYPERV_check_owner_option_by_cli(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg = "Option --hyperv-owner (or VIRTWHO_HYPERV_OWNER environment variable) needs to be set"
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            self.runcmd_service("stop_virtwho")

            # (1) When "--hyperv-owner" is not exist, virt-who should show error info
            cmd_without_owner = "virt-who --hyperv --hyperv-env=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % (hyperv_env, hyperv_server, hyperv_username, hyperv_password) + " -o -d"
            self.vw_check_message(cmd_without_owner, error_msg, cmd_retcode=1)
            # (2) When "--hyperv-owner" with wrong config, virt-who should show error info
            cmd_with_wrong_owner = "virt-who --hyperv --hyperv-owner=%s --hyperv-env=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % ("xxxxxxx", hyperv_env, hyperv_server, hyperv_username, hyperv_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_owner, error_msg, cmd_retcode=1)
            # (3) When "--hyperv-owner" with correct config, virt-who should show error info
            cmd = "virt-who --hyperv --hyperv-owner=%s --hyperv-env=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % (hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
