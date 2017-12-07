from utils import *
from testcases.virt_who_polarion.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID82523_ESX_check_config_options(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.set_esx_conf()

            # (1) Check "VIRTWHO_DEBUG"
            # (1.1) Check "DEBUG" info is exist when run enable "VIRTWHO_DEBUG" in /etc/sysconfig/virt-who
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.vw_check_message_in_rhsm_log("DEBUG")
            self.runcmd_service("stop_virtwho")
            # (1.2) Check "DEBUG" info is not exist when run disable "VIRTWHO_DEBUG" in /etc/sysconfig/virt-who
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            self.vw_check_message_in_rhsm_log("DEBUG", message_exists=False)
            self.vw_check_message_in_rhsm_log("hypervisors and|guests found")
            # (1.3) Set config to VIRTWHO_DEBUG=1
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)

            # (2) Check "VIRTWHO_ONE_SHOT"
            # (2.1) Enable VIRTWHO_ONE_SHOT, check h/g mapping info show only once
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.config_option_setup_value("VIRTWHO_ONE_SHOT", 1)
            tmp_file = "/tmp/tail.rhsm.log"
            self.generate_tmp_log("restart_virtwho", tmp_file)
            cmd = "cat %s" % tmp_file
            self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)
            # (2.2) Disable VIRTWHO_ONE_SHOT
            self.config_option_disable("VIRTWHO_ONE_SHOT")
            self.runcmd_service("restart_virtwho")

            # (3) Check "VIRTWHO_INTERVAL"
            # (3.1) Disable VIRTWHO_INTERVAL and Check virt-who refresh default interval is 60s
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            check_msg = self.get_vw_cons("vw_interval_check_msg")
            check_default_interval = self.get_vw_cons("vm_default_interval_msg")

            self.vw_check_message_number_in_rhsm_log(check_default_interval, 1, 150)
            # (3.2) Check virt-who refresh interval is 60 when config interval less than 60s
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(check_msg, 2, 150)
            # (3.3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(check_msg, 1, 150)

            # (4).Check virt-who thread will not increase after restart it.
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                if self.virtwho_version[9:13] > 0.20:
                    self.check_virtwho_thread(2)
                else:
                    self.check_virtwho_thread(1)
                time.sleep(5)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_setup_value("VIRTWHO_DEBUG", 1)
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.config_option_disable("VIRTWHO_ONE_SHOT")
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
