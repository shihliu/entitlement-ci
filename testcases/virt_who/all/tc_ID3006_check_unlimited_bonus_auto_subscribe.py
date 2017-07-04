from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID3006_check_unlimited_bonus_auto_subscribe(VIRTWHOBase):
    def run_kvm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_bonus_name")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
            self.runcmd_service("restart_virtwho")

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku)
            # (1). guest auto subscribe bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_auto_subscribe(guestip)
            # (2). Check consumed subscriptions' name on guest
            self.check_consumed_status(guest_bonus_sku, "SubscriptionName", sku_name, guestip)
            # (3). check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
        finally:
            self.sub_unregister(guestip)
            # unsubscribe host
            self.sub_unsubscribe()
            self.vw_stop_guests(guest_name)
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            guest_name = self.get_vw_guest_name("KVM_GUEST_NAME")
            remote_ip_1 = get_exported_param("REMOTE_IP_1")
            guestuuid = self.vw_get_uuid(guest_name, remote_ip_1)
            host_uuid = self.get_host_uuid(remote_ip_1)
            host_name = self.get_hostname(remote_ip_1)
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_bonus_name")

            self.vw_start_guests(guest_name, remote_ip_1)
            guestip = self.kvm_get_guest_ip(guest_name, remote_ip_1)
            self.runcmd_service("restart_virtwho")

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe the hypervisor to the physical pool which can generate bonus pool
            if "stage" in SERVER_TYPE:
                self.server_subscribe_system(host_name, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            else:
                self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # (1). guest auto subscribe bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_auto_subscribe(guestip)
            # (2). Check consumed subscriptions' name on guest
            self.check_consumed_status(guest_bonus_sku, "SubscriptionName", sku_name, guestip)
            # (3). check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
        finally:
            self.sub_unsubscribe()
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # register hypervisor
            if "stage" in SERVER_TYPE:
                self.server_unsubscribe_all_system(host_name, SERVER_IP)
            else:
                self.server_unsubscribe_all_system(host_uuid, SERVER_IP)
            self.runcmd_service("restart_virtwho")
            self.vw_stop_guests(guest_name, remote_ip_1)
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku)
            # (1). guest auto subscribe bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_auto_subscribe(guestip)
            # (2). Check consumed subscriptions' name on guest
            self.check_consumed_status(guest_bonus_sku, "SubscriptionName", sku_name, guestip)
            # (3). check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
        finally:
            # unsubscribe host and stop guest
            self.sub_unsubscribe()
            self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
#             sku_name = self.get_vw_cons("datacenter_name")
            sku_name = self.get_vw_cons("datacenter_bonus_name")

            self.vw_restart_virtwho()

            # (1) Start guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_uuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            # (2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            self.sub_disable_auto_subscribe(guestip)
            # (3) Subscribe hypervisor
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(test_sku), server_ip)
            # (4) Guest auto subscribe
            self.sub_unsubscribe(guestip)
            self.sub_auto_subscribe(guestip)
            # (5) list consumed subscriptions on the guest, should be listed
            self.check_consumed_status(guest_bonus_sku, "SubscriptionName", sku_name, guestip)
        finally:
#             if guestip != None and guestip != "":
#                 self.sub_unregister(guestip)
#             self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            host_uuid = self.hyperv_get_host_uuid()

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
#             sku_name = self.get_vw_cons("datacenter_name")
            sku_name = self.get_vw_cons("datacenter_bonus_name")

            self.vw_restart_virtwho()

            # (1) Start guest
            self.hyperv_start_guest(guest_name)
            guestip = self.hyperv_get_guest_ip(guest_name)
            # (2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            self.sub_disable_auto_subscribe(guestip)
            # (3) Subscribe hypervisor
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(test_sku), server_ip)
            # (4) Guest auto subscribe
            self.sub_unsubscribe(guestip)
            self.sub_auto_subscribe(guestip)
            # (5) list consumed subscriptions on the guest, should be listed
            self.check_consumed_status(guest_bonus_sku, "SubscriptionName", sku_name, guestip)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.hyperv_stop_guest(guest_name)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)

            sku_id = self.get_vw_cons("datacenter_sku_id")
            sku_bonus_id = self.get_vw_cons("datacenter_bonus_sku_id")
#             sku_name = self.get_vw_cons("datacenter_name")
            sku_name = self.get_vw_cons("datacenter_bonus_name")
            sku_quantity = self.get_vw_cons("datacenter_bonus_quantity")

            self.vw_restart_virtwho()

            # start guest
            if self.esx_guest_ispoweron(guest_name, esx_host_ip):
                self.esx_stop_guest(guest_name, esx_host_ip)
            self.esx_start_guest(guest_name, esx_host_ip)
            guestip = self.esx_get_guest_ip(guest_name, esx_host_ip)

            # register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            self.sub_disable_auto_subscribe(guestip)

            # subscribe esx host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), server_ip)
            # list available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_bonus_id, sku_quantity, guestip)
            self.sub_unsubscribe(guestip)
            self.sub_auto_subscribe(guestip)

            # list consumed subscriptions on the guest, should be listed
            self.sub_listconsumed(sku_name, guestip)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            self.esx_stop_guest(guest_name, esx_host_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            server_ip, server_hostname, server_type, server_user, server_pass = self.get_server_info()
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            host_uuid = self.xen_get_host_uuid(xen_host_ip)

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
#             sku_name = self.get_vw_cons("datacenter_name")
            sku_name = self.get_vw_cons("datacenter_bonus_name")

            # (1) Start guest
            self.xen_start_guest(guest_name, xen_host_ip)
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)

            self.vw_restart_virtwho()

            # (2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            self.sub_disable_auto_subscribe(guestip)
            # (3) Subscribe hypervisor
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(test_sku), server_ip)
            # (4) Guest auto subscribe
            self.sub_unsubscribe(guestip)
            self.sub_auto_subscribe(guestip)
            # (5) list consumed subscriptions on the guest, should be listed
            self.check_consumed_status(guest_bonus_sku, "SubscriptionName", sku_name, guestip)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
#             self.xen_stop_guest(guest_name, xen_host_ip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
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
