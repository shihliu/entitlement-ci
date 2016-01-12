from utils import *
from testcases.virt_who.kvmbase import KVMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17252_check_uuid_fake_remote_libvird(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_ip = get_exported_param("REMOTE_IP")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            VIRTWHO_TYPE="libvirt"
            VIRTWHO_SERVER = "qemu+ssh://" + remote_ip + "/system"
            remote_owner = self.get_vw_cons("VIRTWHO_LIBVIRT_OWNER")
            remote_env = self.get_vw_cons("VIRTWHO_LIBVIRT_ENV")
            remote_user = self.get_vw_cons("VIRTWHO_LIBVIRT_USERNAME")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake"

            # define a guest
            self.vw_define_guest(guest_name)
            guestuuid = self.vw_get_uuid(guest_name)

            # stop virt-who service on host1 and host2
            self.vw_stop_virtwho_new()
            self.vw_stop_virtwho_new(remote_ip_2)
            # configure remote libvirt mode on host2
            self.set_virtwho_sec_config(VIRTWHO_TYPE, VIRTWHO_SERVER, remote_user, "", remote_owner, remote_env, remote_ip_2)

            # (1) generate fake file
            self.generate_fake_file("kvm", fake_file, remote_ip_2)
            # (3) check if guest uuid is correctly monitored by virt-who.
            self.unset_virtwho_d_conf("/etc/virt-who.d/virt-who", remote_ip_2 )

            # (4) configure fake mode on host2
            self.set_fake_mode_conf(fake_file, "True", remote_owner, remote_env, remote_ip_2)

#             check if guest uuid is correctly monitored by virt-who.
#             check_msg = "Sending update in hosts-to-guests mapping: 1 hypervisors and 1 guests found"
#             self.vw_check_message_in_rhsm_log(check_msg, targetmachine_ip=remote_ip_2)
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=remote_ip_2)
            # (5) check if error message will show on log file 
            self.vw_check_message_in_rhsm_log('Using configuration "fake"', targetmachine_ip=remote_ip_2)

            # define a guest
            self.vw_undefine_guest(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=remote_ip_2)

            self.unset_virtwho_d_conf(fake_config_file, remote_ip_2)

            # (4) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "False", remote_owner, remote_env, remote_ip_2)
            # (5) check if error message will show on log file 
            self.vw_check_message_in_rhsm_log("is not properly formed: 'uuid'", remote_ip_2)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            self.unset_virtwho_d_conf(fake_file, remote_ip_2)
            self.unset_virtwho_d_conf(fake_config_file, remote_ip_2)
            self.unset_virtwho_d_conf("/etc/virt-who.d/virt-who", remote_ip_2 )
            self.vw_restart_virtwho_new()
            self.vw_restart_virtwho_new(remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
