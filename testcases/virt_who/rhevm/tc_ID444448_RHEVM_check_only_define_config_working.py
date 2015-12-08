from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID444448_RHEVM_check_only_define_config_working(VDSMBase):
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
            conf_file = "/etc/virt-who.d/rhevm"

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            #1). stop virt-who firstly 
            self.service_command("stop_virtwho")
            #2). disable rhevm in /etc/sysconfig/virt-who
            cmd = "sed -i -e 's/.*VIRTWHO_RHEVM=.*/#VIRTWHO_RHEVM=1/g' /etc/sysconfig/virt-who"
            ret, output = self.runcmd(cmd, "Configure virt-who to disable VIRTWHO_RHEVM")
            if ret == 0:
                logger.info("Succeeded to disable VIRTWHO_RHEVM.")
            else:
                raise FailException("Test Failed - Failed to disable VIRTWHO_RHEVM.")
            #3). creat /etc/virt-who.d/rhevm file for rhevm mode
            conf_data = '''[rhevm-test]
type=rhevm
server=%s
username=%s
password=%s
owner=%s
env=%s''' % (VIRTWHO_RHEVM_SERVER_2, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_PASSWORD, VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV)
            self.set_virtwho_d_conf(conf_file, conf_data)
            #4). after stop virt-who, start to monitor the rhsm.log 
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            cmd = "tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            self.runcmd(cmd, "generate nohup.out file by tail -f")
            #5). virt-who restart
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running with the right encrypted_password.")
            else:
                raise FailException("Failed to check, virt-who should become running or active with an right encrypted_password.")
            #6).# check only /etc/virt-who.d/XXX  has been used
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "feedback tail log for parse")
            if guestuuid in output and 'Using configuration "env/cmdline" ("rhevm" mode)' not in output and 'Using configuration "rhevm-test" ("rhevm" mode)':
                logger.info("Succeeded to check virt-who only run at defined modes.")
            else:
                raise FailException("Failed to check virt-who only run at defined modes.")
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

