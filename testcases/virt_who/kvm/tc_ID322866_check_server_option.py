from utils import *
from testcases.virt_who.kvmbase import KVMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException
import paramiko

class tc_ID322866_check_server_option(KVMBase):
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

            test_server = get_exported_param("SERVER_TYPE")
            VIRTWHO_LIBVIRT_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_OWNER")
            VIRTWHO_LIBVIRT_ENV = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_ENV")
            VIRTWHO_LIBVIRT_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_LIBVIRT_USERNAME")
            VIRTWHO_LIBVIRT_SERVER = "qemu+ssh://" + remote_ip + "/system"

            # stop virt-who service on host1 and host2
            self.vw_stop_virtwho_new()
            self.vw_stop_virtwho_new(remote_ip_2)

            # check option of --satellite6 and --sam
            if test_server == "SATELLITE":
                cmd = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password= --satellite6 -o -d" % (VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV, VIRTWHO_LIBVIRT_SERVER, VIRTWHO_LIBVIRT_USERNAME)
                ret, output = self.runcmd(cmd, "run --satellite6 in CLI", targetmachine_ip=remote_ip_2)
                if ret == 0 and guestuuid in output:
                    logger.info("Succeeded to check --satellite6 option")
                else:
                    raise FailException("Test Failed - Failed to check --satellite6 option")
            else:
                cmd = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password= --sam -o -d" % (VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV, VIRTWHO_LIBVIRT_SERVER, VIRTWHO_LIBVIRT_USERNAME)
                ret, output = self.runcmd(cmd, "run --sam in CLI", targetmachine_ip=remote_ip_2)
                if ret == 0 and guestuuid in output:
                    logger.info("Succeeded to check --sam option")
                else:
                    raise FailException("Test Failed - Failed to check --sam option")
            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_restart_virtwho_new()
            self.vw_restart_virtwho_new(remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
