from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17263_validate_compliance_check_uuid_when_migrate_guest_to_unsubscribe_host(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()

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
            # (1).subscribe host to the physical pool and guest subscribe bonus pool
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            self.sub_listconsumed(sku_name, guestip)
            before_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)

            # (2) check if the uuid is exist before migrate guest .
            self.vw_check_uuid(guestuuid, uuidexists=True)

            # (3) migrate guest to slave machine
            self.vw_migrate_guest(guest_name, slave_machine_ip)

            # (4) Check guest uuid in original host and destination host
            self.vw_check_uuid(guestuuid, uuidexists=False)
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=slave_machine_ip)

            # (5).after migration,list consumed subscriptions on guest
            after_poolid = self.sub_check_consumed_pool(guest_bonus_sku, key="PoolID", targetmachine_ip=guestip)
            self.sub_check_bonus_pool_after_migate(before_poolid, after_poolid, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # unsubscribe host
            self.sub_unsubscribe()
            self.sub_unsubscribe(slave_machine_ip)
            self.vw_define_guest(guest_name)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.vw_stop_guests(guest_name, slave_machine_ip)
            self.vw_undefine_guest(guest_name, slave_machine_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
