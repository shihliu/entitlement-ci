from utils import *
from testcases.virt_who.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17262_validate_compliance_check_att_after_pause_shutdown_guest(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)

            # (1).check if the uuid and attributes are correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 1, guestuuid)

            # (2). register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            #(3).subscribe host to the physical pool and guest subscribe bonus pool
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            self.sub_listconsumed(sku_name, guestip)

            # (4). pause guest    
            self.pause_vm(guest_name)
            # (5).check if the uuid and attributes are correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 3, guestuuid)

            # (6). resume guest    
            self.resume_vm(guest_name)
    
            # (7).Check consumed subscriptions on guest
            self.check_consumed_status(test_sku, "SubscriptionName", sku_name, guestip)

            # (8)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 1, guestuuid)

            # (9) stop guest    
            self.vw_stop_guests(guest_name)

            # (10)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 0, 'libvirt', 'QEMU', 5, guestuuid)

            # (11).restart guest 
            self.vw_start_guests(guest_name)
            time.sleep(20)

            # (12).Check consumed subscriptions on guest
            self.check_consumed_status(test_sku, "SubscriptionName", sku_name, guestip)

            # (13)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'libvirt', 'QEMU', 1, guestuuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.vw_stop_guests(guest_name)
            # unsubscribe host
            self.sub_unsubscribe()
            self.vw_define_all_guests()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
