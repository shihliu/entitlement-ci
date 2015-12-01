from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID289675_RHEVM_Datacenter_repos_in_host_and_guest(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # subscribe the hypervisor to the physical pool which can generate bonus pool
            self.server_subscribe_system(hostuuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)

            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)

            # Check repositories available in guest
            cmd = "subscription-manager repos --list | grep -A4 \"^Repo ID\""
            ret, output = self.runcmd(cmd, "Check repositories available in guest", guestip)
            if ret == 0 and "This system has no repositories available through subscriptions." not in output:
                logger.info("Succeeded to check repositories available in guest.")
            else:
                raise FailException("Failed to check repositories available in guest.")
            # Check content sets exist in cert file in guest
            cmd = "rct cat-cert /etc/pki/entitlement/*[^-key].pem | grep -A11 \"^Content:\""
            ret, output = self.runcmd(cmd, "Check content sets exist in cert file in guest", guestip)
            if ret == 0:
                logger.info("Succeeded to check content sets exist in cert file in guest.")
            else:
                raise FailException("Failed to check content sets exist in cert file in guest..")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unsubscribe all subscriptions on  hypervisor
            self.server_unsubscribe_all_system(hostuuid, SERVER_IP)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
