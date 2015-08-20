from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException
import paramiko

class tc_ID476491_check_offline_mode(VIRTWHOBase):
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
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")
            VIRTWHO_LIBVIRT_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_OWNER")
            VIRTWHO_LIBVIRT_ENV = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_ENV")
            VIRTWHO_LIBVIRT_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_USERNAME")
            VIRTWHO_LIBVIRT_SERVER = "qemu+ssh://" + remote_ip + "/system"
            VIRTWHO_FAKE_FILE = "/home/fake"

            # stop virt-who service on host1
            self.vw_stop_virtwho_new()
            # configure remote libvirt mode on host2
            self.clean_remote_libvirt_conf(remote_ip_2)
            self.vw_stop_virtwho_new(remote_ip_2)

            # generate remote libvirt mapping info to /home/fake
            cmd = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password= -p -d > %s" % (VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV, VIRTWHO_LIBVIRT_SERVER, VIRTWHO_LIBVIRT_USERNAME, VIRTWHO_FAKE_FILE)
            ret, output = self.runcmd(cmd, targetmachine_ip=remote_ip_2)
            if ret == 0 :
                logger.info("Succeeded to generate info which used to make virt-who run at fake mode")
            else:
                raise FailException("Test Failed - Failed to generate info which used to make virt-who run at fake mode")

            self.sub_unregister()

            # creat /etc/virt-who.d/fake file which make virt-who run at fake mode
            conf_file = "/etc/virt-who.d/fake"
            conf_data = '''[fake]
type=fake
file=%s
is_hypervisor=True
owner=%s
env=%s''' % (VIRTWHO_FAKE_FILE, VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV)

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
            self.sub_register(SAM_USER, SAM_PASS)
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
