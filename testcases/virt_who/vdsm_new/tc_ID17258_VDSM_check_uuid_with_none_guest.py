from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17258_VDSM_check_uuid_with_none_guest(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            rhevm_ip = get_exported_param("RHEVM_IP")
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")

            cmd = "rhevm-shell -c -E 'show vm %s'" % guest_name
            ret, output = self.runcmd(cmd, "list vm in rhevm.", rhevm_ip)
            vm_status = self.get_key_rhevm(output, "status-state", "name", guest_name, rhevm_ip)
            if ret == 0 :
                if vm_status.find("down") >= 0:
                    logger.info("Succeeded to list vm in poweroff in rhevm.")
                else:
                    logger.info("vm is still running in rhevm.")
                    self.rhevm_stop_vm(guest_name, rhevm_ip)
            else:
                raise FailException("Failed to list vm in rhevm.")
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid("", uuidexists=True)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
