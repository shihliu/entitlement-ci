from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID2011_check_guest_att_after_resume_pause_poweroff_poweron(VIRTWHOBase):
    def run_kvm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)

            # (1).check if the uuid and attributes are correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 1, guestuuid)

            # (2).register guest to Server
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # (3).subscribe host to the physical pool and guest subscribe bonus pool
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            self.sub_listconsumed(sku_name, guestip)

            # (4).pause guest    
            self.pause_vm(guest_name)
            # (5).check if the uuid and attributes are correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
#             self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 3, guestuuid)
            self.vw_check_attr(guest_name, 1, 'libvirt', 3, guestuuid)
            # (6).resume guest    
            self.resume_vm(guest_name)

            # (7) check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 1, guestuuid)

            # (8).Check consumed subscriptions on guest
            self.check_consumed_status(test_sku, "SubscriptionName", sku_name, guestip)

            # (9) stop guest    
            self.vw_stop_guests(guest_name)

            # (10)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 0, 'libvirt', 5, guestuuid)

            # (11).restart guest 
            self.vw_start_guests(guest_name)
            time.sleep(20)

            # (12)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 1, guestuuid)

            # (13).Check consumed subscriptions on guest
            self.check_consumed_status(test_sku, "SubscriptionName", sku_name, guestip)
        finally:
            self.vw_define_all_guests()
            # unsubscribe host
            self.sub_unsubscribe()
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
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
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # (1).check if the uuid and attributes are correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'vdsm', 1, guestuuid)

            # (2). register guest to Server
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # (3).subscribe host to the physical pool and guest subscribe bonus pool
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            self.sub_listconsumed(sku_name, guestip)

            # (4). pause guest   
            self.rhevm_pause_vm(guest_name, rhevm_ip)

            # (5).check if the uuid and attributes are correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False)

            # (6).Pause host1 and make guest move to host2
            
            # (6). resume guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)

            # (7)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
#             self.vw_check_attr(guest_name, 1, 'vdsm', 'qemu', 1, guestuuid)
            self.vw_check_attr(guest_name, 1, 'vdsm', 1, guestuuid)

            # (8).Check consumed subscriptions on guest
            self.check_consumed_status(test_sku, "SubscriptionName", sku_name, guestip)

            # (9) stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)

            # (10)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False)

            # (11).restart guest 
            self.rhevm_start_vm(guest_name, rhevm_ip)

            # (12)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'vdsm', 1, guestuuid)

            # (13).Check consumed subscriptions on guest
            self.check_consumed_status(test_sku, "SubscriptionName", sku_name, guestip)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
#             unsubscribe host
            self.sub_unsubscribe()
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            orig_host_name = self.get_hostname(get_exported_param("REMOTE_IP"))
            dest_host_ip = get_exported_param("REMOTE_IP_2")
            dest_host_name = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")

            self.vw_restart_virtwho()

            # (1) Register guest to SAM and subscribe to the bonus pool
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe the hypervsior1 to the physical pool which can generate bonus pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (2) Start guest , check guest's uuid and guest's attribute 
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=True)
#             self.vw_check_attr(guest_name, 1, 'rhevm', 'qemu', 1, guestuuid)
            self.vw_check_attr(guest_name, 1, 'rhevm', 1, guestuuid)
            # (3) Pause guest    
            self.rhevm_pause_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=False)
            # (4) Resume guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who on host1 and host2
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'rhevm', 1, guestuuid)
            # consumed subscriptions is still exist on guest
            self.sub_listconsumed(sku_name, guestip)
            # (5) Stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=False)
        finally:
            self.rhevm_start_vm(guest_name, rhevm_ip)
            if guestip != None and guestip != "":
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
            self.hyperv_start_guest(guest_name)
            guestip = self.hyperv_get_guest_ip(guest_name)

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")

            self.vw_restart_virtwho()

            # (1) Register guest to SAM and subscribe to the bonus pool
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe the hypervsior1 to the physical pool which can generate bonus pool
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (2) Start guest , check guest's uuid and guest's attribute 
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
#             self.vw_check_attr(guest_name, 1, 'hyperv', 'hyperv', 1, guest_uuid)
            self.vw_check_attr(guest_name, 1, 'hyperv', 1, guest_uuid)
            # (3) Pause guest    
            self.hyperv_suspend_guest(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'hyperv', 3, guest_uuid)
            # (4) Resume guest    
            self.hyperv_resume_guest(guest_name)
            # check if the uuid is correctly monitored by virt-who on host1 and host2
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'hyperv', 1, guest_uuid)

            # consumed subscriptions is still exist on guest
            self.sub_listconsumed(sku_name, guestip)
            # (5) Stop guest    
            self.hyperv_stop_guest(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
            self.vw_check_attr(guest_name, 0, 'hyperv', 5, guest_uuid)
        finally:
            self.hyperv_start_guest(guest_name)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
#             self.hyperv_stop_guest(guest_name)
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            esx_host_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(esx_host_ip)
            guest_uuid = self.esx_get_guest_uuid(guest_name, esx_host_ip)

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")
            sku_quantity = self.get_vw_cons("guestlimit_unlimited_guest")

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
            # list available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, sku_quantity, guestip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            # list consumed subscriptions on the guest, should be listed
            self.sub_listconsumed(sku_name, guestip)

            self.esx_pause_guest(guest_name, esx_host_ip)
            self.runcmd_service("restart_virtwho")
#             self.vw_check_attr(guest_name, 1, "esx", "VMware ESXi", 3, guest_uuid)
            self.vw_check_attr(guest_name, 1, "esx", 3, guest_uuid)
            self.esx_resume_guest(guest_name, esx_host_ip)
            self.runcmd_service("restart_virtwho")
            self.vw_check_attr(guest_name, 1, "esx", 1, guest_uuid)
            # refresh on the guest 
            self.sub_refresh(guestip)
            # list consumed subscriptions on the guest, should be not revoked
            self.sub_listconsumed(sku_name, guestip)
            self.esx_stop_guest(guest_name, esx_host_ip)
            self.runcmd_service("restart_virtwho")
            self.vw_check_attr(guest_name, 0, "esx", 5, guest_uuid)
            self.esx_start_guest(guest_name, esx_host_ip)
            self.runcmd_service("restart_virtwho")
            self.vw_check_attr(guest_name, 1, "esx", 1, guest_uuid)
            # refresh on the guest 
            self.sub_refresh(guestip)
            # list consumed subscriptions on the guest, should be not revoked
            self.sub_listconsumed(sku_name, guestip)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            self.esx_stop_guest(guest_name, esx_host_ip)
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)
            self.xen_start_guest(guest_name, xen_host_ip)
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")

            self.vw_restart_virtwho()

            # (1) Register guest to SAM and subscribe to the bonus pool
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe the hypervsior1 to the physical pool which can generate bonus pool
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (2) Start guest , check guest's uuid and guest's attribute 
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
#             self.vw_check_attr(guest_name, 1, 'xen', 'xen', 1, guest_uuid)
            self.vw_check_attr(guest_name, 1, 'xen', 1, guest_uuid)
            # (3) Pause guest    
            self.xen_suspend_guest(guest_name, xen_host_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=False)
            # (4) Resume guest    
            self.xen_resume_guest(guest_name, xen_host_ip)
            # check if the uuid is correctly monitored by virt-who on host1 and host2
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'xen', 1, guest_uuid)
            # consumed subscriptions is still exist on guest
            self.sub_listconsumed(sku_name, guestip)
            # (5) Stop guest    
            self.xen_stop_guest(guest_name, xen_host_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=False)
        finally:
            self.xen_start_guest(guest_name, xen_host_ip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.xen_stop_guest(guest_name, xen_host_ip)
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
