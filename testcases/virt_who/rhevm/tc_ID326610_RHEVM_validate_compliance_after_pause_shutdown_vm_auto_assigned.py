from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID326610_RHEVM_validate_compliance_after_pause_shutdown_vm_auto_assigned(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            orig_host_name = self.get_hostname(get_exported_param("REMOTE_IP"))
            dest_host_ip = get_exported_param("REMOTE_IP_2")
            dest_host_name = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            dest_host_uuid = self.get_host_uuid_on_rhevm(dest_host_name, rhevm_ip)

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, orig_hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # (1) Restart virt-who and libvirtd service.
            self.vw_restart_virtwho_new()

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe the hypervsior1 to the physical pool which can generate bonus pool
            self.server_subscribe_system(orig_hostuuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)

            # (2) stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)

            # (3) Auto assigned vm to host2
            self.rhevm_mantenance_host(orig_host_name, rhevm_ip)
            # (4) resume guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, auto_hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            # list consumed subscriptions on guest, bonus pool from original host should revoke.
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            # subscribe the hypervsior1 to the physical pool which can generate bonus pool
            self.server_subscribe_system(auto_hostuuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)

            # (5) pause guest    
            self.rhevm_pause_vm(guest_name, rhevm_ip)

            # (6) Active host1
            self.rhevm_active_host(orig_host_name, rhevm_ip)

            # (7) start guest, guest move back to host1    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # list consumed subscriptions on guest, bonus pool from destination host should revoke.
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # Active host1
            self.rhevm_active_host(orig_host_name, rhevm_ip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # unregister the hypervisor1 and hypervisor2
            self.server_unsubscribe_all_system(orig_hostuuid, SERVER_IP)
            self.server_unsubscribe_all_system(auto_hostuuid, SERVER_IP)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
