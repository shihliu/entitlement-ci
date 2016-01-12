from utils import *
from testcases.virt_who.kvmbase import KVMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID475862_check_running_mode(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_ip = get_exported_param("REMOTE_IP")
            username = "root"
            password = "red2015"
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            VIRTWHO_LIBVIRT_OWNER = self.get_vw_cons("VIRTWHO_LIBVIRT_OWNER")
            VIRTWHO_LIBVIRT_ENV = self.get_vw_cons("VIRTWHO_LIBVIRT_ENV")
            VIRTWHO_LIBVIRT_USERNAME = self.get_vw_cons("VIRTWHO_LIBVIRT_USERNAME")
            VIRTWHO_LIBVIRT_SERVER = "qemu+ssh://" + remote_ip + "/system"
            rhsmlogfile = "/var/log/rhsm/rhsm.log"

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

            # configure remote libvirt mode on host2
            self.set_remote_libvirt_conf(remote_ip, remote_ip_2)
            # check running mode 
            cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f", remote_ip_2)
            # ignore restart virt-who serivce since virt-who -b -d will stop
            self.vw_restart_virtwho_new(remote_ip_2)
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "get log number added to rhsm.log", remote_ip_2)
            if ret == 0:
                if "Sending list of uuids: " in output or " Sending update in hosts-to-guests mapping:" in output:
                    if ('Using configuration "remote_libvirt"') in output and ('Using configuration "env/cmdline" ("libvirt" mode)' in output):
                        logger.info("Succeeded to check running mode from rhsm.log.")
                    else:
                        raise FailException("Test Failed - Failed check running mode from rhsm.log.")
                else :
                    raise FailException("Test Failed - Failed to run virt-who service")
            else:
                raise FailException("Failed to get rhsm.log")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file, remote_ip_2)
            self.clean_remote_libvirt_conf(remote_ip_2)
            self.vw_restart_virtwho_new(remote_ip_2)
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
