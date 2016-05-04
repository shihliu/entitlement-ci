from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID17229_VDSM_check_uuid_after_re_register_two_diff_mode(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            mode="rhevm"

            # (1) stop virt-who service
            self.runcmd_service("stop_virtwho")
            # (2) on host2, configure remote rhevm mode in config file /etc/virt-who.d/virtwho
            self.set_virtwho_sec_config(mode)
            # (3) check if two modes are correctly monitored by virt-who.
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.hypervisor_check_uuid(hostuuid, guestuuid)
            # (4) Check guest uuid after unregister host and hypervisor
            tmp_file = "/tmp/tail.rhsm.log"
            cmd = "subscription-manager unregister"
            self.generate_tmp_log(cmd, tmp_file)
            cmd = "cat %s" % tmp_file
            ret, output = self.runcmd(cmd, "get temporary log generated")
            if ret == 0 and ("not registered" in output or "Successfully un-registered" in output):
                logger.info("Success to check virt-who log after unregister host")
            else:
                raise FailException("failed to check virt-who log after unregister host")
            self.server_remove_system(hostuuid, SERVER_IP)
            # (5) Check guest uuid after re-register
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.unset_all_virtwho_d_conf()
            self.runcmd_service("restart_virtwho")
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
