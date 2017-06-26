from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17265_VDSM_validate_compliance_check_uuid_after_ping_pong_migrate(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            orig_host_name = self.get_hostname(get_exported_param("REMOTE_IP"))
            dest_host_name = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            dest_host_uuid = self.get_host_uuid_on_rhevm(dest_host_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, orig_host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # (1).original host,check if the guest uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)

            # (2).subscribe host to the physical pool and guest subscribe bonus pool
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            self.sub_listconsumed(sku_name, guestip)
            before_migrate_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)

            # (3).dest host,check if the guest uuid is not monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False, targetmachine_ip=get_exported_param("REMOTE_IP_2"))

            # (4).migrate guest from original host to dest host
            self.rhevm_migrate_vm(guest_name, dest_host_name , dest_host_uuid, rhevm_ip)

            # (5).After migration,check if the guest uuid is not monitored by virt-who in original host
            self.vw_check_uuid(guestuuid, uuidexists=False)

            # (6).After migration,check if the guest uuid is correctly monitored by virt-who in destination host
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=get_exported_param("REMOTE_IP_2"))

            # (7).after migration, list consumed subscriptions on guest
            after_migrate_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)
            self.sub_check_bonus_pool_after_migate(before_migrate_poolid, after_migrate_poolid, guestip)
#             self.sub_listconsumed(sku_name, guestip, productexists=False)

            # (8).dest host, subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku, get_exported_param("REMOTE_IP_2"))
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            before_migrate_back_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)

            # (9). migrate guest back( from destination host to original host)
            self.rhevm_migrate_vm(guest_name, orig_host_name , orig_host_id, rhevm_ip)

            # (10). list consumed subscriptions on guest
            self.sub_refresh(guestip)
#             self.sub_listconsumed(sku_name, guestip, productexists=False)
            after_migrate_back_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)
            self.sub_check_bonus_pool_after_migate(before_migrate_back_poolid, after_migrate_back_poolid, guestip)

            # (11).After migration back,check if the guest uuid is correctly monitored by virt-who in original host
            self.vw_check_uuid(guestuuid, uuidexists=True)

            # (12).After migration,check if the guest uuid is not monitored by virt-who in destination host
            self.vw_check_uuid(guestuuid, uuidexists=False, targetmachine_ip=get_exported_param("REMOTE_IP_2"))

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
