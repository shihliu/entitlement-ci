from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17216_ESX_check_env_option_by_cli(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg = "Option --esx-env (or VIRTWHO_ESX_ENV environment variable) needs to be set"
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            cmd_without_env = "virt-who --esx --esx-owner=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_message(cmd_without_env, error_msg, cmd_retcode=1)
            cmd_with_wrong_env = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, "xxxxxxx", esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_env, error_msg, cmd_retcode=1)
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
