from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17214_ESX_check_owner_option_by_config(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            cmd_without_owner = "virt-who --esx --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_env, esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_message(cmd_without_owner, "Option --esx-owner (or VIRTWHO_ESX_OWNER environment variable) needs to be set", cmd_retcode=1)
            cmd_with_wrong_owner = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % ("xxxxxxx", esx_env, esx_server, esx_username, esx_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_owner, "", cmd_retcode=1)
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
