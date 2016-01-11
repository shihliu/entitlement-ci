from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17253_VDSM_check_uuid_fake_local_vdsm_mode(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            VIRTWHO_OWNER = self.get_vw_cons("VIRTWHO_LIBVIRT_OWNER")
            VIRTWHO_ENV = self.get_vw_cons("VIRTWHO_LIBVIRT_ENV")
            fake_file = "/tmp/fake_file"
            fake_config_file = "/etc/virt-who.d/fake"

            # define a guest
            self.rhevm_start_vm(guest_name, rhevm_ip)
            # stop virt-who service
            self.vw_stop_virtwho_new()

            # (1) generate fake file
            self.generate_fake_file("vdsm", fake_file)

            # (2) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "False", VIRTWHO_OWNER, VIRTWHO_ENV)

            # (3) check if guest uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.unset_virtwho_d_conf(fake_config_file)

            # (4) configure fake mode on host1
            self.set_fake_mode_conf(fake_file, "True", VIRTWHO_OWNER, VIRTWHO_ENV)
            # (5) check if error message will show on log file 
            self.vw_check_message_in_rhsm_log("is not properly formed: 'uuid'")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.unset_virtwho_d_conf(fake_file)
            self.unset_virtwho_d_conf(fake_config_file)
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
