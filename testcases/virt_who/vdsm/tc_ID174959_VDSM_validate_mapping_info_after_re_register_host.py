from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID174959_VDSM_validate_mapping_info_after_re_register_host(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = VIRTWHOConstants().get_constant("RHEVM_HOST")

            self.conf_rhevm_shellrc(rhevm_ip)
            (guestip,host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # Check guest uuid before unregister
            self.vw_restart_virtwho()
            self.vw_check_uuid(guestuuid, uuidexists=True)
            # Check guest uuid after unregister
            cmd = "subscription-manager unregister"
            ret, output = self.runcmd(cmd, "unreigster system")
            if ret == 0 :
                cmd = "tail -3 /var/log/rhsm/rhsm.log"
                ret, output = self.runcmd(cmd, "check log after unreigster host")
                if ret == 0 and "not registered" in output:
                    logger.info("Success to check virt-who log after unregister host")
                else:
                    raise FailException("failed to check virt-who log after unregister host")
            else:
                raise FailException("failed to unregister host")
            # Check guest uuid after re-register
            self.sub_register(SAM_USER, SAM_PASS)
            self.vw_restart_virtwho()
            self.vw_check_uuid(guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_register(SAM_USER, SAM_PASS)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
