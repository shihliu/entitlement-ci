from utils import *
from testcases.virt_who.kvmbase import KVMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException
import paramiko

class tc_ID439632_validate_remote_libvirt_unlimited_bonus_pool(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")

            test_sku = VIRTWHOConstants().get_constant("productid_unlimited_guest")
            bonus_quantity = VIRTWHOConstants().get_constant("guestlimit_unlimited_guest")
            sku_name = VIRTWHOConstants().get_constant("productname_unlimited_guest")

            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_ip = get_exported_param("REMOTE_IP")
            username = "root"
            password = "red2015"
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            self.vw_start_guests(guest_name)
            guestip = self.kvm_get_guest_ip(guest_name)

            # stop virt-who service on host1
            self.vw_stop_virtwho_new()
            # configure remote libvirt mode on host2
            self.set_remote_libvirt_conf(remote_ip, remote_ip_2)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            self.clean_remote_libvirt_conf(remote_ip_2)
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
