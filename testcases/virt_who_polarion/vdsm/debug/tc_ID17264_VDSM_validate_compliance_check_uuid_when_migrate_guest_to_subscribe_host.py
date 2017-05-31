from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17264_VDSM_validate_compliance_check_uuid_when_migrate_guest_to_subscribe_host(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            dest_host_name = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            dest_host_uuid = self.get_host_uuid_on_rhevm(dest_host_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

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

            # (1).check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # (2).subscribe host to the physical pool and guest subscribe bonus pool
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            self.sub_listconsumed(sku_name, guestip)
            before_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)

#             (3).subscribe dest host to the physical pool and guest subscribe bonus pool before migration
            self.sub_subscribe_sku(test_sku, targetmachine_ip=get_exported_param("REMOTE_IP_2"))
# 
            # (4).migrate guest from host1 to host2
            self.rhevm_migrate_vm(guest_name, dest_host_name , dest_host_uuid, rhevm_ip)

            # (5).check if the uuid is correctly monitored by virt-who in host1 and host2.
            self.vw_check_uuid(guestuuid, uuidexists=False)
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=get_exported_param("REMOTE_IP_2"))
# 
            # (6).after migration,list consumed subscriptions on guest
            after_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)
            self.sub_check_bonus_pool_after_migate(before_poolid, after_poolid, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # unsubscribe host1 and host2
            self.sub_unsubscribe()
            self.sub_unsubscribe(get_exported_param("REMOTE_IP_2"))
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
