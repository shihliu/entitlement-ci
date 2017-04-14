from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17251_VDSM_validate_compliance_revoke_after_unregister_fake_vdsm_mode(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            VIRTWHO_OWNER = self.get_vw_cons("server_owner")
            VIRTWHO_ENV = self.get_vw_cons("server_env")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake"

            test_sku = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # start guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
    
            # stop virt-who service
            self.vw_stop_virtwho()

            # (1) generate fake file
            self.generate_fake_file("vdsm", fake_file)

            # (2) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "False", VIRTWHO_OWNER, VIRTWHO_ENV)

            # (3) restart virt-who service and make virt-who run at fake mode
            self.runcmd_service("restart_virtwho")
            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (4) subscribe the host to the physical pool which can generate bonus pool
            self.sub_subscribe_sku(test_sku)
            # (5) subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(test_sku, guestip)
            # (6) list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (7) unregister hosts
            self.sub_unregister()
            self.sub_refresh(guestip)
            # (8) list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.sub_unregister(guestip)
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.unset_virtwho_d_conf(fake_file)
            self.unset_virtwho_d_conf(fake_config_file)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
