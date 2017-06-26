from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID0002_check_register_host_guest_with_cli(VIRTWHOBase):
    def run_kvm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            # (1) Unregister host and configure kvm
            self.sub_unregister()
            self.update_vw_configure()
            # (2) Register host to server and check host/guest mapping info
            register_cmd = "subscription-manager register --username=%s --password=%s" % (SERVER_USER, SERVER_PASS)
            self.vw_check_uuid(guestuuid, checkcmd=register_cmd, uuidexists=True)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.runcmd_service("stop_virtwho")
            for i in range(1, 5):
                self.vw_check_mapping_info_number("virt-who --vdsm -o -d", 1)
            self.check_virtwho_thread(0)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            # (1) Unregister host and configure rhevm
            self.sub_unregister()
            self.set_rhevm_conf()
            # (2) Register host to server and check host/guest mapping info
            register_cmd = "subscription-manager register --username=%s --password=%s" % (SERVER_USER, SERVER_PASS)
            self.hypervisor_check_uuid(hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd=register_cmd, uuidexists=True)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            guestuuid = self.hyperv_get_guest_guid(guest_name)
            hostuuid = self.hyperv_get_host_uuid()

            # (1) Unregister host and configure hyperv
            self.sub_unregister()
            self.set_hyperv_conf()
            # (2) Register host to server and check host/guest mapping info
            register_cmd = "subscription-manager register --username=%s --password=%s" %(SERVER_USER, SERVER_PASS)
            self.hypervisor_check_uuid(hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd=register_cmd, uuidexists=True)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            guestuuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            hostuuid = self.esx_get_host_uuid(esx_host_ip)

            # (1) Unregister host and configure esx
            self.sub_unregister()
            self.set_esx_conf()
            # (2) Register host to server and check host/guest mapping info
            register_cmd = "subscription-manager register --username=%s --password=%s" %(SERVER_USER, SERVER_PASS)
            self.hypervisor_check_uuid(hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd=register_cmd, uuidexists=True)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)
            # (1) Unregister host and configure xen
            self.sub_unregister()
            self.set_xen_conf()
            # (2) Register host to server and check host/guest mapping info
            self.xen_start_guest(guest_name, xen_host_ip)
            register_cmd = "subscription-manager register --username=%s --password=%s" %(SERVER_USER, SERVER_PASS)
            self.hypervisor_check_uuid(host_uuid, guest_uuid, rhsmlogpath='/var/log/rhsm', checkcmd=register_cmd, uuidexists=True)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
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