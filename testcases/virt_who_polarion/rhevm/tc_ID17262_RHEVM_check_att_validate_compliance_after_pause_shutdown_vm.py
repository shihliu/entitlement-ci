from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17262_RHEVM_check_att_validate_compliance_after_pause_shutdown_vm(VDSMBase):
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

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_start_vm(guest_name, rhevm_ip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
