from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID322864_VDSM_check_log_small_interval_after_add_guest(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = self.get_vw_cons("RHEVM_HOST")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)

            rhsmlogpath = '/var/log/rhsm/rhsm.log'

            # config the virt-who config file, set VIRTWHO_INTERVAL = 2
            self.update_rhevm_vdsm_configure(2)
            # .restart virtwho service
            self.vw_restart_virtwho_new()
            # start a guest    
            self.rhevm_start_vm(guest_name, rhevm_ip)
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            # check virt-who log
            cmd = "tail -50 %s " % rhsmlogpath
            ret, output = self.runcmd(cmd, "check output in rhsm.log")
            if ret == 0 and ("AttributeError" not in output) and ("propSet" not in output) and ("Exception:" not in output):
                logger.info("Success to check virt-who log normally after add a new guest.")
            else:
                raise FailException("Failed to check virt-who log normally after add a new guest.")
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            #stop guest    
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            # set interval to default : 5
            self.update_rhevm_vdsm_configure(5)
            # .restart virtwho service
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
