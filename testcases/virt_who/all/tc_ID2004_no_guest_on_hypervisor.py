from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID2004_no_guest_on_hypervisor(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.vw_undefine_all_guests()
            # (1)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid("", uuidexists=True)
        finally:
            self.vw_define_all_guests()
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            shell_cmd = self.get_rhevm_shell(rhevm_ip)
            get_vm_cmd = self.get_vm_cmd(guest_name, rhevm_ip)

            cmd = "%s -c -E '%s'" % (shell_cmd, get_vm_cmd)
            ret, output = self.runcmd(cmd, "list vm in rhevm.", rhevm_ip)
            vm_status = self.get_key_rhevm(output, "status-state", "name", guest_name, rhevm_ip)
            if ret == 0 :
                if vm_status.find("down") >= 0:
                    logger.info("Succeeded to list vm in poweroff in rhevm.")
                else:
                    logger.info("vm is still running in rhevm.")
                    self.rhevm_stop_vm(guest_name, rhevm_ip)
            else:
                raise FailException("Failed to list vm in rhevm.")
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid("", uuidexists=True)
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_uuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.vw_check_mapping_info_in_rhsm_log("", guest_uuid, uuid_exist=False)
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.skipTest("test case skiped, not fit for hyperv ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)

            self.esx_remove_guest(guest_name, esx_host_ip)
            self.vw_check_mapping_info_in_rhsm_log("", guest_uuid, uuid_exist=False)
        finally:
            self.esx_add_guest(guest_name, esx_host_ip)
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

# template for platform not related cases
# class tc_ID0000_template(VIRTWHOBase):
#     def test_run(self):
#         case_name = self.__class__.__name__
#         logger.info("========== Begin of Running Test Case %s ==========" % case_name)
#         try:
#             pass
#             self.assert_(True, case_name)
#         except Exception, SkipTest:
#             logger.info(str(SkipTest))
#             raise SkipTest
#         except Exception, e:
#             logger.error("Test Failed - ERROR Message:" + str(e))
#             self.assert_(False, case_name)
#         finally:
#             logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
