from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17265_validate_compliance_check_uuid_after_ping_pong_migrate(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            master_machine_ip = get_exported_param("REMOTE_IP")
            slave_machine_ip = get_exported_param("REMOTE_IP_2")

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_sku(test_sku, slave_machine_ip)

            # (1).subscribe host to the physical pool and guest subscribe bonus pool
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            self.sub_listconsumed(sku_name, guestip)
            before_migrate_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)

            # (2) check if the uuid is exist before migrate guest .
            self.vw_check_uuid(guestuuid, uuidexists=True)

            # (3) migrate guest to slave machine
            self.vw_migrate_guest(guest_name, slave_machine_ip)

            # (4).after migration,list consumed subscriptions on guest
            after_migrate_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)
            self.sub_check_bonus_pool_after_migate(before_migrate_poolid, after_migrate_poolid, guestip)

            # (5) after migration, Check guest uuid in original host and destination host
            self.vw_check_uuid(guestuuid, uuidexists=False)
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=slave_machine_ip)

            # (6).dest host, subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku, get_exported_param("REMOTE_IP_2"))
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            before_migrate_back_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)

           # (7). migrate guest back( from destination host to original host)
            self.vw_migrate_guest(guest_name, master_machine_ip, slave_machine_ip)

            # (8).After migration back,check if the guest uuid is correctly monitored by virt-who in original host
            self.vw_check_uuid(guestuuid, uuidexists=True)

            # (9).After migration,check if the guest uuid is not monitored by virt-who in destination host
            self.vw_check_uuid(guestuuid, uuidexists=False, targetmachine_ip=get_exported_param("REMOTE_IP_2"))

            # (10). list consumed subscriptions on guest
            after_migrate_back_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)
            self.sub_check_bonus_pool_after_migate(before_migrate_back_poolid, after_migrate_back_poolid, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # unsubscribe host
            self.sub_unsubscribe()
            self.sub_unsubscribe(slave_machine_ip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.vw_stop_guests(guest_name)
            self.vw_define_guest(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
