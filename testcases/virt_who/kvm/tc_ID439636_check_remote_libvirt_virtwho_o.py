from utils import *
from testcases.virt_who.kvmbase import KVMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException
import paramiko

class tc_ID439636_check_remote_libvirt_virtwho_o(KVMBase):
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
            remote_owner = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_OWNER")
            remote_env = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_ENV")
            remote_user = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_USERNAME")

            # stop virt-who service on host1 and host2
            self.vw_stop_virtwho_new()
            self.vw_stop_virtwho_new(remote_ip_2)
            # On host2, run virt-who at remote libvirt mode at one-shot mode
            cmd = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password= -o -d" %(remote_owner, remote_env, remote_ip, remote_user)
            ret, output = self.runcmd(cmd, "Run virt-who at one-shot mode in remote libvirt mode", remote_ip_2)
            if ret == 0:
                if ("Sending domain info" in output or "Sending list of uuids" in output or "Sending update in hosts-to-guests mapping" in output) and guestuuid in output and "ERROR" not in output:
                    logger.info("Succeeded to check log when run virt-who -o -d in remote libvirt mode.")
                else:
                    raise FailException("Failed to check log when run virt-who -o -d in remote libvirt mode.")
            else:
                raise FailException("Failed to run virt-who -o -d in remote libvirt mode.")
            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # restart virt-who service on host1 and host2
            self.vw_restart_virtwho_new()
            self.vw_restart_virtwho_new(remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
