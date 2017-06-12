from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID3016_datacenter_check_guest_compliance_with_multi_sockets(VIRTWHOBase):
    def run_kvm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")

            host_test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
            self.runcmd_service("restart_virtwho")

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # host subscribe datacenter pool
            self.sub_subscribe_sku(host_test_sku)
            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4", guestip)

            # (1).subscribe guest to unspecify datacenter pool
            gpoolid = self.get_pool_by_SKU(guest_bonus_sku, guestip)
            self.sub_subscribetopool(gpoolid, guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(guest_bonus_sku, "StatusDetails", "Subscription is current", guestip)
            # .check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)

            # (2).subscribe the registered guest to 1 bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(gpoolid, "1", guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # .check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
        finally:
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unsubscribe host
            self.sub_unsubscribe()
            self.vw_stop_guests(guest_name)
            logger.info("---------- succeed to restore environment ----------")

    def run_remote_libvirt(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            host_test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # host subscribe datacenter pool
            self.sub_subscribe_sku(host_test_sku)
            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4", guestip)

            # (1).subscribe guest to unspecify datacenter pool
            gpoolid = self.get_pool_by_SKU(guest_bonus_sku, guestip)
            self.sub_subscribetopool(gpoolid, guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(guest_bonus_sku, "StatusDetails", "Subscription is current", guestip)
            # .check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)

            # (2).subscribe the registered guest to 1 bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(gpoolid, "1", guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # .check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
        finally:
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unsubscribe host
            self.sub_unsubscribe()
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            host_test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            self.vw_restart_virtwho()

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # host subscribe datacenter pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(host_test_sku), SERVER_IP)
            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4", guestip)

            # (1) Subscribe guest to unspecify datacenter pool
            gpoolid = self.get_pool_by_SKU(guest_bonus_sku, guestip)
            self.sub_subscribetopool(gpoolid, guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(guest_bonus_sku, "StatusDetails", "Subscription is current", guestip)
            # .check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)

            # (2) Subscribe the registered guest to 1 bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(gpoolid, "1", guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
        finally:
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # unsubscribe all subscriptions on  hypervisor
            self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
            host_test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            self.vw_restart_virtwho()

            self.hyperv_start_guest(guest_name)
            guestip = self.hyperv_get_guest_ip(guest_name)
            hostuuid = self.hyperv_get_host_uuid()

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # host subscribe datacenter pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(host_test_sku), SERVER_IP)
            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4", guestip)

            # (1) Subscribe guest to unspecify datacenter pool
            gpoolid = self.get_pool_by_SKU(guest_bonus_sku, guestip)
            self.sub_subscribetopool(gpoolid, guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(guest_bonus_sku, "StatusDetails", "Subscription is current", guestip)
            # .check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
            # (2) Subscribe the registered guest to 1 bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(gpoolid, "1", guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
        finally:
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.hyperv_stop_guest(guest_name)
            # unsubscribe all subscriptions on  hypervisor
            self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)

            sku_id = self.get_vw_cons("datacenter_sku_id")
            sku_bonus_id = self.get_vw_cons("datacenter_bonus_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")
            sku_quantity = self.get_vw_cons("datacenter_bonus_quantity")

            self.setup_custom_facts("cpu.cpu_socket(s)", "4")

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

            # subscribe esx host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), server_ip)
            self.check_bonus_exist(sku_bonus_id, sku_quantity, guestip)

            gpoolid = self.get_pool_by_SKU(sku_bonus_id, guestip)

            self.sub_subscribetopool(gpoolid, guestip)
            # list consumed subscriptions on the guest, should be listed
            self.sub_listconsumed(sku_name, guestip)

            self.check_consumed_status(sku_bonus_id, "QuantityUsed", "1", guestip)
            self.check_installed_status("Status", "Subscribed", guestip)

            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(gpoolid, "1", guestip)

            self.check_consumed_status(sku_bonus_id, "QuantityUsed", "1", guestip)
            self.check_installed_status("Status", "Subscribed", guestip)
        finally:
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            self.esx_stop_guest(guest_name, esx_host_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            host_test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            self.vw_restart_virtwho()

            self.xen_start_guest(guest_name, xen_host_ip)
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)
            hostuuid = self.xen_get_host_uuid(xen_host_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # host subscribe datacenter pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(host_test_sku), SERVER_IP)
            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "4", guestip)

            # (1) Subscribe guest to unspecify datacenter pool
            gpoolid = self.get_pool_by_SKU(guest_bonus_sku, guestip)
            self.sub_subscribetopool(gpoolid, guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(guest_bonus_sku, "StatusDetails", "Subscription is current", guestip)
            # .check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
            # (2) Subscribe the registered guest to 1 bonus pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(gpoolid, "1", guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(guest_bonus_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
        finally:
            self.restore_facts(guestip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
#             self.xen_stop_guest(guest_name, xen_host_ip)
            # unsubscribe all subscriptions on  hypervisor
            self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
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
