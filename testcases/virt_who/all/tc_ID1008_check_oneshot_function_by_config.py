from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1008_check_oneshot_function_by_config(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.config_option_setup_value("VIRTWHO_ONE_SHOT", 1)
            tmp_file = "/tmp/tail.rhsm.log"
            self.generate_tmp_log("restart_virtwho", tmp_file)
            cmd = "cat %s" % tmp_file
            self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)
        finally:
            self.config_option_disable("VIRTWHO_ONE_SHOT")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.config_option_setup_value("VIRTWHO_ONE_SHOT", 1)
            tmp_file = "/tmp/tail.rhsm.log"
            self.generate_tmp_log("restart_virtwho", tmp_file)
            cmd = "cat %s" % tmp_file
            self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)
        finally:
            self.config_option_disable("VIRTWHO_ONE_SHOT")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Enable VIRTWHO_ONE_SHOT, check h/g mapping info show only once
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.config_option_setup_value("VIRTWHO_ONE_SHOT", 1)
            tmp_file = "/tmp/tail.rhsm.log"
            self.generate_tmp_log("restart_virtwho", tmp_file)
            cmd = "cat %s" % tmp_file
            self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)
        finally:
            self.config_option_disable("VIRTWHO_ONE_SHOT")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Enable VIRTWHO_ONE_SHOT, check h/g mapping info show only once
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.config_option_setup_value("VIRTWHO_ONE_SHOT", 1)
            tmp_file = "/tmp/tail.rhsm.log"
            self.generate_tmp_log("restart_virtwho", tmp_file)
            cmd = "cat %s" % tmp_file
            self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)
        finally:
            self.config_option_disable("VIRTWHO_ONE_SHOT")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.config_option_setup_value("VIRTWHO_ONE_SHOT", 1)
            tmp_file = "/tmp/tail.rhsm.log"
            self.generate_tmp_log("restart_virtwho", tmp_file)
            cmd = "cat %s" % tmp_file
            self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)
        finally:
            self.config_option_disable("VIRTWHO_ONE_SHOT")
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Enable VIRTWHO_ONE_SHOT, check h/g mapping info show only once
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.config_option_setup_value("VIRTWHO_ONE_SHOT", 1)
            tmp_file = "/tmp/tail.rhsm.log"
            self.generate_tmp_log("restart_virtwho", tmp_file)
            cmd = "cat %s" % tmp_file
            self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)
        finally:
            self.config_option_disable("VIRTWHO_ONE_SHOT")
            self.runcmd_service("restart_virtwho")
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
