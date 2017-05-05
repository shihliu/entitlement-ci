from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17260_check_uuid_after_add_vm_restart_libvirtd(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 60)
            self.runcmd_service("restart_virtwho")
            cmd_stop_guest = "virsh destroy %s" % guest_name

            self.vw_start_guests(guest_name)

            # (1) start guest then check if the uuid is correctly monitored by virt-who.
            self.vw_check_message_in_rhsm_log("Using libvirt url", checkcmd="service libvirtd restart")
            self.vw_check_uuid(guestuuid, uuidexists=True, checkcmd=cmd_stop_guest)
            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
            # (2). register guest to Server
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (3).subscribe host to the physical pool and guest subscribe bonus pool
            self.sub_subscribe_sku(test_sku)
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            self.sub_listconsumed(sku_name, guestip)
            # (4) Restart libvirtd service then check if the uuid is correctly monitored by virt-who
            self.vw_check_message_in_rhsm_log(guestuuid, checkcmd="service libvirtd restart")
            # (5) restart guest then check bonus pool is not revoke. 
            self.sub_listconsumed(sku_name, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.vw_stop_guests(guest_name)
            # unsubscribe host
            self.sub_unsubscribe()
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
