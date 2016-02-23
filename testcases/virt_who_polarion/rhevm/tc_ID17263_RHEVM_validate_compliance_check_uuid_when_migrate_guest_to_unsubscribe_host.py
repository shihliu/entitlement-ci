from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17263_RHEVM_validate_compliance_check_uuid_when_migrate_guest_to_unsubscribe_host(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            orig_host_name = self.get_hostname(get_exported_param("REMOTE_IP"))
            rhevm_ip = get_exported_param("RHEVM_IP")
            dest_ip = get_exported_param("REMOTE_IP_2")
            dest_host_name = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            dest_host_uuid = self.get_host_uuid_on_rhevm(dest_host_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

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
            before_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)
            # (2) Migrate guest from host1 to host2
            self.rhevm_migrate_vm(guest_name, dest_host_name , dest_host_uuid, rhevm_ip)
            # (3) Check guest uuid in original host and destination host
            self.vw_check_uuid(guestuuid, uuidexists=False)
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=dest_ip)
            # (4) After migration,list consumed subscriptions on guest
            after_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)
            self.sub_check_bonus_pool_after_migate(before_poolid, after_poolid, guestip)
            (guestip, auto_hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # unsubscribe all subscriptions on  hypervisor1 and hypervisor2
            self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
            self.server_unsubscribe_all_system(auto_hostuuid, SERVER_IP)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
