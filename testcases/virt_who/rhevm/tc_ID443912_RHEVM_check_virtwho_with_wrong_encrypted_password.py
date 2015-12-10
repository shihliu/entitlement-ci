from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID443912_RHEVM_check_virtwho_with_wrong_encrypted_password(VDSMBase):
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
            conf_data = '''[rhevm]
type=rhevm
server=%s
username=%s
encrypted_password=aaaaaaaa
owner=%s
env=%s''' % (VIRTWHO_RHEVM_SERVER_2, VIRTWHO_RHEVM_USERNAME, VIRTWHO_RHEVM_OWNER, VIRTWHO_RHEVM_ENV)
            self.set_virtwho_d_conf(conf_file, conf_data)
            #4). after stop virt-who, start to monitor the rhsm.log 
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            cmd = "tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            self.runcmd(cmd, "generate nohup.out file by tail -f")
            #5). virt-who restart
            if self.service_command("restart_virtwho", is_return=True) == False:
                logger.info("Succeeded to check, virt-who restart failed with an error encrypted_password.")
                virtwho_status = self.check_virtwho_status()
                if virtwho_status == "failed" or virtwho_status == "stopped" or virtwho_status == "unknown":
                    logger.info("Succeeded to check, virt-who status is failed with an error encrypted_password.")
                else:
                    raise FailException("Failed to check, virt-who shouldn't become running or active with an error encrypted_password.")
            else:
                raise FailException("Failed to check, virt-who service should not be restarted with an wrong encrypted_password.")
            #6). after restart virt-who, stop to monitor the rhsm.log
            time.sleep(5)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "feedback tail log for parse")
            if "ERROR" in output or (hostuuid in output and guestuuid in output):
                logger.info("Succeeded to check, virt-who run error and no uuid found wtih an error encrypted_password.")
            else:
                raise FailException("Failed to check, virt-who should run error and no uuid found with an error encrypted_password.")
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

