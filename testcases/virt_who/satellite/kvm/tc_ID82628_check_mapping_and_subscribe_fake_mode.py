from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID82628_check_mapping_and_subscribe_fake_mode(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_ip = get_exported_param("REMOTE_IP")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guest_uuid = self.vw_get_uuid(guest_name)
            host_uuid = self.get_host_uuid()
            mode="libvirt"
            VIRTWHO_SERVER = "qemu+ssh://" + remote_ip + "/system"
            virtwho_owner = self.get_vw_cons("server_owner")
            virtwho_env = self.get_vw_cons("server_env")
            remote_user = self.get_vw_cons("VIRTWHO_LIBVIRT_USERNAME")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake.conf"

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            bonus_quantity = self.get_vw_cons("guestlimit_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")

            # (1) Check mapping info in fake mode
            # (1.1) Unregister kvm hypervisor in server 
            self.vw_stop_virtwho()
            self.vw_stop_virtwho(remote_ip_2)
            
            self.server_remove_system(host_uuid, SERVER_IP)
            # (1.2) Set kvm fake mode, it will show host/guest mapping info
            self.set_virtwho_sec_config(mode, remote_ip_2)
            self.generate_fake_file("kvm", fake_file, remote_ip_2)
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.set_fake_mode_conf(fake_file, "True", virtwho_owner, virtwho_env, remote_ip_2)
            # (1.3) check if guest uuid is correctly monitored by virt-who.
#             self.vw_check_message_in_rhsm_log("%s" % guest_uuid, message_exists=True, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (1.4) check if virt-who run at fake mode 
            self.vw_check_message_in_rhsm_log('Using configuration "fake"', targetmachine_ip=remote_ip_2)
            
            # (2) Check bonus pool will created in fake mode
            # (2.1) Start guest and register guest to SAM
            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # (2.2) Subscribe fake kvm host
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), SERVER_IP)
            # (2.3) List available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, bonus_quantity, guestip)
            self.sub_subscribe_to_bonus_pool(sku_id, guestip)
            self.sub_listconsumed(sku_name, guestip)

            # (3) Check bonus pool will revoke in fake mode
            # (3.1) Unsubscribe sku on hypervisor
            self.server_unsubscribe_all_system(host_uuid, SERVER_IP)
            # (3.2) Check consumed bonus pool revoke on guest
            self.sub_refresh(guestip)
            self.sub_listconsumed(sku_name, guestip, productexists=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.server_remove_system(host_uuid, SERVER_IP)
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
