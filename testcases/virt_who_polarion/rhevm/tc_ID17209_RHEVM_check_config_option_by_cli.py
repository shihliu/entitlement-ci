from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17209_RHEVM_check_config_option_by_cli(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_RHEVM")

#           (1) Check virt-who send h/g mapping info one time when run "virt-who -c "
            conf_file = "/etc/virt-who.d/virt-who.conf"
            self.set_virtwho_sec_config("rhevm")
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
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
