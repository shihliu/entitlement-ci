from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1073_check_bonus_revoke_in_fake_mode(VIRTWHOBase):
    def run_kvm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            VIRTWHO_OWNER = self.get_vw_cons("server_owner")
            VIRTWHO_ENV = self.get_vw_cons("server_env")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake.conf"

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # start guest
            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
    
            # stop virt-who service
            self.vw_stop_virtwho()

            # (1) generate fake file
            self.generate_fake_file("kvm", fake_file)

            # (2) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "False", VIRTWHO_OWNER, VIRTWHO_ENV)

            # (3) restart virt-who service and make virt-who run at fake mode
            self.vw_restart_virtwho()
            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (4) subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku)
            # (5) subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # (6) list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (7) unregister hosts
            self.sub_unregister()
            self.sub_refresh(guestip)
            # (8) list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip, productexists=False)
        finally:
            self.sub_unregister(guestip)
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.vw_stop_guests(guest_name)
            self.unset_virtwho_d_conf(fake_file)
            self.unset_virtwho_d_conf(fake_config_file)
            self.vw_restart_virtwho()
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            VIRTWHO_OWNER = self.get_vw_cons("server_owner")
            VIRTWHO_ENV = self.get_vw_cons("server_env")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake.conf"

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # start guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
    
            # stop virt-who service
            self.vw_stop_virtwho()

            # (1) generate fake file
            self.generate_fake_file("vdsm", fake_file)

            # (2) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "False", VIRTWHO_OWNER, VIRTWHO_ENV)

            # (3) restart virt-who service and make virt-who run at fake mode
            self.vw_restart_virtwho()
            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (4) subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku)
            # (5) subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # (6) list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (7) unregister hosts
            self.sub_unregister()
            self.sub_refresh(guestip)
            # (8) list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip, productexists=False)
        finally:
            self.sub_unregister(guestip)
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.unset_virtwho_d_conf(fake_file)
            self.unset_virtwho_d_conf(fake_config_file)
            self.vw_restart_virtwho()
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_uuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # (1) Unregister rhevm hypervisor in server 
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_RHEVM")
            self.server_remove_system(host_uuid, SERVER_IP)
            # (2) Register rhevm hypervisor with fake mode
            fake_file = self.generate_fake_file("rhevm")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Register guest to Server
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (4) Subscribe fake rhevm host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), SERVER_IP)
            # (5) List available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, bonus_quantity, guestip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            self.sub_listconsumed(sku_name, guestip)
            # (6) Unregister fake rhevm hypervisor in server 
            self.runcmd_service("stop_virtwho")
            self.server_remove_system(host_uuid, SERVER_IP)
            # (7) Check consumed bonus pool revoke on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            hyperv_host_ip = self.get_vw_cons("HYPERV_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()
            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # (1) Unregister hyperv hypervisor in server 
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_HYPERV")
            self.server_remove_system(host_uuid, SERVER_IP)
            # (2) Register hyperv hypervisor with fake mode
            fake_file = self.generate_fake_file("hyperv")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Start guest and register guest to SAM
            self.hyperv_start_guest(guest_name)
            guestip = self.hyperv_get_guest_ip(guest_name)
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (4) Subscribe fake hyperv host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), SERVER_IP)
            # (5) List available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, bonus_quantity, guestip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            self.sub_listconsumed(sku_name, guestip)
            # (6) Unregister fake hyperv hypervisor in server 
            self.runcmd_service("stop_virtwho")
            self.server_remove_system(host_uuid, SERVER_IP)
            # (7) Check consumed bonus pool revoke on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)
        finally:
            self.sub_unregister(guestip)
            self.hyperv_stop_guest(guest_name)
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.runcmd_service("stop_virtwho")
            self.unset_esx_conf()
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)
            fake_file = self.generate_fake_file("esx")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")
            sku_quantity = self.get_vw_cons("guestlimit_unlimited_guest")

            # start guest
            if self.esx_guest_ispoweron(guest_name, esx_host_ip):
                self.esx_stop_guest(guest_name, esx_host_ip)
            self.esx_start_guest(guest_name, esx_host_ip)
            guestip = self.esx_get_guest_ip(guest_name, esx_host_ip)

            # register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)

            # subscribe esx host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), server_ip)

            # list available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, sku_quantity, guestip)

            self.sub_subscribe_to_bonus_pool(sku_id, guestip)

            # list consumed subscriptions on the guest, should be listed
            self.sub_listconsumed(sku_name, guestip)

            # unregister host from SAM server.
            self.server_unsubscribe_all_system(host_uuid, server_ip)

            # refresh on the guest 
            self.sub_refresh(guestip)

            # check bonus pool is revoked on guest
            self.check_bonus_exist(sku_id, sku_quantity, guestip, bonus_exist=False)

            # list consumed subscriptions on the guest, should be revoked
            self.sub_listconsumed(sku_name, guestip, productexists=False)
# 
#             # check the status of installed product, should be "Not Subscribed"
#             self.check_installed_status("Status", "Not Subscribed", guestip)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            self.esx_stop_guest(guest_name, esx_host_ip)
            self.unset_all_virtwho_d_conf()
            self.set_esx_conf()
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)
            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")

            self.xen_start_guest(guest_name, xen_host_ip)

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # (1) Unregister xen hypervisor in server 
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_XEN")
            self.server_remove_system(host_uuid, SERVER_IP)
            # (2) Register xen hypervisor with fake mode
            fake_file = self.generate_fake_file("xen")
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (3) Start guest and register guest to SAM
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (4) Subscribe fake xen host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), SERVER_IP)
            # (5) List available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, bonus_quantity, guestip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            self.sub_listconsumed(sku_name, guestip)
            # (6) Unregister fake xen hypervisor in server 
            self.runcmd_service("stop_virtwho")
            self.server_remove_system(host_uuid, SERVER_IP)
            # (7) Check consumed bonus pool revoke on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)
        finally:
            self.sub_unregister(guestip)
            self.xen_stop_guest(guest_name, xen_host_ip)
            self.unset_all_virtwho_d_conf()
            self.set_xen_conf()
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
