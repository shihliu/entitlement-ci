from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1075_check_fake_mode_for_local_libvirt_in_virtwho_d(VIRTWHOBase):
    def run_kvm(self):
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            VIRTWHO_OWNER = self.get_vw_cons("server_owner")
            VIRTWHO_ENV = self.get_vw_cons("server_env")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake.conf"

            # define a guest
            self.vw_define_guest(guest_name)
            guestuuid = self.vw_get_uuid(guest_name)
            self.vw_stop_virtwho()

            # (1) generate fake file
            self.generate_fake_file("kvm", fake_file)

            # (2) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "False", VIRTWHO_OWNER, VIRTWHO_ENV)

            # (3) check if guest uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.unset_virtwho_d_conf(fake_config_file)

            # (4) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "True", VIRTWHO_OWNER, VIRTWHO_ENV)
            # (5) check if error message will show on log file 
            self.vw_check_message_in_rhsm_log("is not properly formed: 'uuid'")
        finally:
            self.vw_define_all_guests()
            self.unset_virtwho_d_conf(fake_file)
            self.unset_all_virtwho_d_conf()
            self.vw_restart_virtwho()
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
            remote_ip_1 = get_exported_param("REMOTE_IP_1")
            host_uuid = self.get_host_uuid(remote_ip_1)
            guest_uuid = self.vw_get_uuid(guest_name, remote_ip_1)

            VIRTWHO_OWNER = self.get_vw_cons("server_owner")
            VIRTWHO_ENV = self.get_vw_cons("server_env")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake.conf"
            self.config_option_disable("VIRTWHO_LIBVIRT")

            # define a guest
            self.vw_define_guest(guest_name, remote_ip_1)
            self.runcmd_service("stop_virtwho")

            # (1) generate fake file
            self.generate_fake_file("libvirt", fake_file)

            # (2) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "True", VIRTWHO_OWNER, VIRTWHO_ENV)

            # (3) check if guest uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guest_uuid, uuidexists=True)
            self.unset_virtwho_d_conf(fake_config_file)

            # (4) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "False", VIRTWHO_OWNER, VIRTWHO_ENV)
            # (5) check if error message will show on log file 
            self.vw_check_message_in_rhsm_log("is not properly formed: 'uuid'|try to check is_hypervisor value")
        finally:
            self.vw_define_all_guests(remote_ip_1)
            self.unset_virtwho_d_conf(fake_file)
            self.unset_all_virtwho_d_conf()
            self.config_option_enable("VIRTWHO_LIBVIRT")
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            VIRTWHO_OWNER = self.get_vw_cons("server_owner")
            VIRTWHO_ENV = self.get_vw_cons("server_env")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake.conf"

            # define a guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # stop virt-who service
            self.vw_stop_virtwho()

            # (1) generate fake file
            self.generate_fake_file("vdsm", fake_file)

            # (2) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "False", VIRTWHO_OWNER, VIRTWHO_ENV)

            # (3) check if guest uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.unset_virtwho_d_conf(fake_config_file)

            # (4) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "True", VIRTWHO_OWNER, VIRTWHO_ENV)
            # (5) check if error message will show on log file 
            self.vw_check_message_in_rhsm_log("is not properly formed: 'uuid'")
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.unset_virtwho_d_conf(fake_file)
            self.unset_virtwho_d_conf(fake_config_file)
            self.vw_restart_virtwho()
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_RHEVM")

            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_uuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # (1) Set rhevm fake mode with is_hypervisor=True, it will not show host/guest mapping info
            self.runcmd_service("stop_virtwho")
            fake_file = self.generate_fake_file("rhevm")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set rhevm fake mode, stop guest, it still show host/guest mapping info
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Set rhevm fake mode with is_hypervisor=False, it will not show host/guest mapping info
            self.runcmd_service("stop_virtwho")
            fake_file = self.generate_fake_file("rhevm")
            self.set_fake_mode_conf(fake_file, "False", virtwho_owner, virtwho_env)
            self.vw_check_message_in_rhsm_log(host_uuid, message_exists=False)
            # (3) Set hyperv fake mode with is_hypervisor=False, it will remind is_hypevisor is not correct
            chkmsg = "uuid key shouldn't be present, try to check is_hypervisor value"
            self.vw_check_message_in_rhsm_log(("%s|is not properly formed" % chkmsg), message_exists=True)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_HYPERV")

            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            hyperv_host_ip = self.get_vw_cons("HYPERV_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()
            
            # (1) Set hyperv fake mode with is_hypervisor=True, it will show host/guest mapping info
            fake_file = self.generate_fake_file("hyperv")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set hyperv fake mode with is_hypervisor=False, it will not show host/guest mapping info
            self.runcmd_service("stop_virtwho")
            fake_file = self.generate_fake_file("hyperv")
            self.set_fake_mode_conf(fake_file, "False", virtwho_owner, virtwho_env)
            self.vw_check_message_in_rhsm_log(host_uuid, message_exists=False)
            # (3) Set hyperv fake mode with is_hypervisor=False, it will remind is_hypevisor is not correct
            chkmsg = "uuid key shouldn't be present, try to check is_hypervisor value"
            self.vw_check_message_in_rhsm_log(("%s|is not properly formed" % chkmsg), message_exists=True)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.skipTest("test case skiped, not fit for esx ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.config_option_disable("VIRTWHO_XEN")

            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)

            self.xen_start_guest(guest_name, xen_host_ip)
            self.runcmd_service("stop_virtwho")

            # (1) Set xen fake mode with is_hypervisor=True, it will show host/guest mapping info
            fake_file = self.generate_fake_file("xen")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Set xen fake mode with is_hypervisor=False, it will not show host/guest mapping info
            self.runcmd_service("stop_virtwho")
            fake_file = self.generate_fake_file("xen")
            self.set_fake_mode_conf(fake_file, "False", virtwho_owner, virtwho_env)
            self.vw_check_message_in_rhsm_log(host_uuid, message_exists=False)
            # (3) Set xen fake mode with is_hypervisor=False, it will remind is_hypevisor is not correct
            chkmsg = "uuid key shouldn't be present, try to check is_hypervisor value"
            self.vw_check_message_in_rhsm_log(("%s|is not properly formed" % chkmsg), message_exists=True)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_xen_conf()
#             self.xen_stop_guest(guest_name, xen_host_ip)
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
