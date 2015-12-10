from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID476491_RHEVM_check_offline_mode(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            VIRTWHO_RHEVM_OWNER = self.get_vw_cons("VIRTWHO_RHEVM_OWNER")
            VIRTWHO_RHEVM_ENV = self.get_vw_cons("VIRTWHO_RHEVM_ENV")
            VIRTWHO_RHEVM_SERVER = "https:\/\/" + rhevm_ip + ":443"
            VIRTWHO_RHEVM_SERVER_2 = "https://" + rhevm_ip + ":443"
            VIRTWHO_RHEVM_USERNAME = self.get_vw_cons("VIRTWHO_RHEVM_USERNAME")
            VIRTWHO_RHEVM_PASSWORD = self.get_vw_cons("VIRTWHO_RHEVM_PASSWORD")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            VIRTWHO_FAKE_FILE = "/home/fake"

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            #1). disable rhevm in /etc/sysconfig/virt-who
            cmd = "sed -i -e 's/.*VIRTWHO_RHEVM=.*/#VIRTWHO_RHEVM=1/g' /etc/sysconfig/virt-who"
            ret, output = self.runcmd(cmd, "Configure virt-who to disable VIRTWHO_RHEVM")
            if ret == 0:
                logger.info("Succeeded to disable VIRTWHO_RHEVM.")
            else:
                raise FailException("Test Failed - Failed to disable VIRTWHO_RHEVM.")

            #2). stop virt-who firstly 
            self.service_command("stop_virtwho")
            # generate remote libvirt mapping info to /home/fake
            cmd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s -p -d > %s" % (VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV, VIRTWHO_RHEVM_SERVER, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_PASSWORD, VIRTWHO_FAKE_FILE)
            ret, output = self.runcmd(cmd)
            if ret == 0 :
                logger.info("Succeeded to generate info which used to make virt-who run at fake mode")
            else:
                raise FailException("Test Failed - Failed to generate info which used to make virt-who run at fake mode")

            # creat /etc/virt-who.d/fake file which make virt-who run at fake mode
            conf_file = "/etc/virt-who.d/fake"
            conf_data = '''[fake]
type=fake
file=%s
is_hypervisor=True
owner=%s
env=%s''' % (VIRTWHO_FAKE_FILE, VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV)

            self.set_virtwho_d_conf(conf_file, conf_data)

            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=True)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            self.update_rhel_rhevm_configure("5", VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV, VIRTWHO_RHEVM_SERVER, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_PASSWORD, debug=1)
            self.service_command("restart_virtwho")
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
