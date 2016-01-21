from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17209_HYPERV_check_config_option_by_cli(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
#           (1) Check virt-who send h/g mapping info one time when run "virt-who -c "
            conf_file = "/etc/virt-who.d/virt-who"
            self.set_virtwho_sec_config("hyperv")
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
#           (2) Check virt-who send h/g mapping info one time when run "virt-who -config "
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
