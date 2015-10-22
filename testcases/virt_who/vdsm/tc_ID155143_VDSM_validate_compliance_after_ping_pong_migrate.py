from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID155143_VDSM_validate_compliance_after_ping_pong_migrate(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = self.get_vw_cons("RHEVM_HOST")
            orig_host_name = self.get_hostname(get_exported_param("REMOTE_IP"))
            dest_host_name = self.get_hostname(get_exported_param("REMOTE_IP_2"))
            dest_host_uuid = self.vdsm_get_host_uuid(dest_host_name, rhevm_ip)

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, orig_host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # In host1, subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
 
            # migrate guest from host1 to host2
            self.rhevm_migrate_vm(guest_name, dest_host_name , dest_host_uuid, rhevm_ip)

            # list consumed subscriptions on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            # In host2, subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku, get_exported_param("REMOTE_IP_2"))
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)

            # migrate guest from host2 to host1
            self.rhevm_migrate_vm(guest_name, orig_host_name , orig_host_id, rhevm_ip)

            # list consumed subscriptions on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)

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
