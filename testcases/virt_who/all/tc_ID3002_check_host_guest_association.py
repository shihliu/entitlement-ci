from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID3002_check_host_guest_association(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.skipTest("test case skiped, not fit for kvm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # (1) Start guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            # (2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            # (3) Check host/guest mappping info
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guestuuid)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            hyperv_host_ip = self.get_vw_cons("HYPERV_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()

            # (1) Start guest
            self.hyperv_start_guest(guest_name)
            guestip = self.hyperv_get_guest_ip(guest_name)
            # (2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            # (3) Check host/guest mappping info
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
        finally:
            self.hyperv_stop_guest(guest_name)
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)

            # start guest
            if self.esx_guest_ispoweron(guest_name, esx_host_ip):
                self.esx_stop_guest(guest_name, esx_host_ip)
            self.esx_start_guest(guest_name, esx_host_ip)
            guestip = self.esx_get_guest_ip(guest_name, esx_host_ip)

            # register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)

            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.esx_stop_guest(guest_name, esx_host_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)

            # (1) Start guest
            self.xen_start_guest(guest_name, xen_host_ip)
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)
            # (2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            # (3) Check host/guest mappping info
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
        finally:
#             self.xen_stop_guest(guest_name, xen_host_ip)
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
