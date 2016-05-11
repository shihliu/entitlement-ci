from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17284_VDSM_validate_datacenter_repos_in_host_and_guest(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            host_test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")
            sku_name = self.get_vw_cons("datacenter_name")

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            self.sub_subscribe_sku(host_test_sku)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)

            # Check certificate information exist in cert file in host
            cmd = "rct cat-cert /etc/pki/entitlement/*[^-key].pem | grep -A7 \"^Certificate:\""
            ret, output = self.runcmd(cmd, "Check certificate information exist in cert file in host")
            if ret == 0 :
                logger.info("Succeeded to check certificate information exist in cert file in host.")
            else:
                raise FailException("Failed to check certificate information exist in cert file in host.")
            # Check content sets not exist in cert file in host
            cmd = "rct cat-cert /etc/pki/entitlement/*[^-key].pem | grep -A11 \"^Content:\""
            ret, output = self.runcmd(cmd, "Check content sets not exist in cert file in host")
            if ret != 0:
                logger.info("Succeeded to check content sets not exist in cert file in host.")
            else:
                raise FailException("Failed to check content sets not exist in cert file in host.")
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
            self.vw_stop_guests(guest_name)
            self.vw_define_guest(guest_name)
            # unsubscribe host
            self.sub_unsubscribe()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
