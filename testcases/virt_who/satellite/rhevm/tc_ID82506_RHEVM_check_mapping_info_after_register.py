from utils import *
# from testcases.virt_who_polarion.vdsmbase import VDSMBase
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID82506_RHEVM_check_mapping_info_after_register(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_TYPE, SERVER_USER, SERVER_PASS = self.get_server_info()
            guest_name = self.get_vw_guest_name("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # (1) Unregister host and configure rhevm
            self.sub_unregister()
            self.set_rhevm_conf()
            # (2) Register host to server and check host/guest mapping info
            register_cmd = "subscription-manager register --username=%s --password=%s" % (SERVER_USER, SERVER_PASS)
            ret, output = self.runcmd(register_cmd, "register system")
            # Check bug 1520762
            if "Host has already been taken" in output:
                register_cmd = "subscription-manager register --username=%s --password=%s" %(SERVER_USER, SERVER_PASS)
                ret, output = self.runcmd(register_cmd, "re-register system")
                logger.info("**********the output info is %s" %output)
            self.sub_unregister()
            self.hypervisor_check_uuid(hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd=register_cmd, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
