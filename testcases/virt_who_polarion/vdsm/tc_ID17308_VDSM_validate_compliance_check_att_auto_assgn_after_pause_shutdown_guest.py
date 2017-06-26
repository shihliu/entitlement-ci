from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17308_VDSM_validate_compliance_check_att_auto_assgn_after_pause_shutdown_guest(VDSMBase):
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

            #(3).subscribe host to the physical pool and guest subscribe bonus pool
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            self.sub_listconsumed(sku_name, guestip)

            # (4). pause guest   
            self.rhevm_pause_vm(guest_name, rhevm_ip)

            # (5).check if the uuid and attributes are correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False)

            # (6). mantenance host1,resume guest make guest move to host2
            self.rhevm_mantenance_host(orig_host_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)

            # (7).check if the uuid is correctly monitored by virt-who on orignal and destination host.
            self.vw_check_uuid(guestuuid, uuidexists=False)
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=dest_host_name)
#             self.vw_check_attr(guest_name, 1, 'vdsm', 'qemu', 1, guestuuid, targetmachine_ip=dest_host_name)
            self.vw_check_attr(guest_name, 1, 'vdsm', 1, guestuuid, targetmachine_ip=dest_host_name)

            # (8).Check consumed subscriptions is revoke on guest 
            self.sub_listconsumed(sku_name, guestip, productexists=False)
            self.sub_subscribe_sku(test_sku, dest_host_name)
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            self.check_consumed_status(test_sku, "SubscriptionName", sku_name, guestip)

            # (9).stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)

            # (10).check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False)
            self.vw_check_uuid(guestuuid, uuidexists=False, targetmachine_ip=dest_host_name)

            # (11).resume host1 and restart guest
            self.rhevm_active_host(orig_host_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)

            # (12)check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'vdsm', 1, guestuuid)

            # (13).Check consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
#             unsubscribe host
            self.sub_unsubscribe()
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
