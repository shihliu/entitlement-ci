from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1018_check_server_option_by_cli(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.runcmd_service("stop_virtwho")
            server_type = get_exported_param("SERVER_TYPE")
            if server_type == "SAM":
                self.vw_check_mapping_info_number("virt-who -o -d --sam", 1)
                self.check_virtwho_thread(0)
            elif server_type == "SATELLITE":
                self.vw_check_mapping_info_number("virt-who -o -d --satellite6", 1)
                self.check_virtwho_thread(0)
            else:
                logger.info("it is %s mode, needn't to run this command" % server_type)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            server_type = get_exported_param("SERVER_TYPE")
            self.rhevm_start_vm(guest_name, rhevm_ip)
            self.runcmd_service("stop_virtwho")
            if server_type == "SAM":
                self.vw_check_mapping_info_number("virt-who -o -d --vdsm --sam", 1)
            elif server_type == "SATELLITE":
                self.vw_check_mapping_info_number("virt-who -o -d --vdsm --satellite6", 1)
            else:
                logger.info("it is %s mode, needn't to run this command" % server_type)
            self.check_virtwho_thread(0)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.skipTest("test case skiped, not fit for rhevm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.skipTest("test case skiped, not fit for hyperv ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.skipTest("test case skiped, not fit for esx ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.skipTest("test case skiped, not fit for xen ...")
        finally:
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
