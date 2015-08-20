from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException
import paramiko

class tc_ID444448_check_use_another_configfile_when_no_config(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_ip = get_exported_param("REMOTE_IP")
            username = "root"
            password = "red2015"
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            VIRTWHO_LIBVIRT_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_OWNER")
            VIRTWHO_LIBVIRT_ENV = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_ENV")
            VIRTWHO_LIBVIRT_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_USERNAME")
            VIRTWHO_LIBVIRT_SERVER = "qemu+ssh://" + remote_ip + "/system"

            # stop virt-who service on host1
            self.vw_stop_virtwho_new()
            # configure remote libvirt mode on host2
            self.clean_remote_libvirt_conf(remote_ip_2)
            # creat /etc/virt-who.d/libvirt.remote file for remote libvirt mode
            conf_file = "/etc/virt-who.d/libvirt.remote"
            conf_data = '''[remote_libvirt]
type=libvirt
server=%s
username=%s
password=
owner=%s
env=%s''' % (VIRTWHO_LIBVIRT_SERVER, VIRTWHO_LIBVIRT_USERNAME, VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV)

            self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip=remote_ip_2)

            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file, remote_ip_2)
            self.vw_restart_virtwho_new(remote_ip_2)
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
