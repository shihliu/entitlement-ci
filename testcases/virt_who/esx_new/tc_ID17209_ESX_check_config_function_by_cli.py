from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID17209_ESX_check_config_function_by_cli(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            self.runcmd_service("stop_virtwho")
            conf_file = "/tmp/esx.conf"
            self.esx_set_config_file(conf_file, esx_owner, esx_env, esx_server, esx_username, esx_password)
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
