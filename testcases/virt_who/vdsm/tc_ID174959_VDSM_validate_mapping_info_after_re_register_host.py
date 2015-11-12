from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID174959_VDSM_validate_mapping_info_after_re_register_host(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")

            self.conf_rhevm_shellrc(rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            # Check guest uuid before unregister
            self.vw_restart_virtwho_new()
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
            self.sub_register(SERVER_USER, SERVER_PASS)
            self.vw_restart_virtwho()
            self.vw_check_uuid(guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            # stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
