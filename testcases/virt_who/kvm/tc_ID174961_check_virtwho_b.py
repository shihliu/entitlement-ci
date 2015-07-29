from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID174961_check_virtwho_b(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            self.vw_stop_virtwho()

            cmd = "virt-who -b -d"
            ret, output = self.runcmd(cmd, "run virt-who -b -d command")
            if ret == 0 :
                # check the status of virt-who
                cmd = "ps -ef | grep virt-who"
                ret, output = self.runcmd(cmd, "check the process of virt-who with background mode")
                if ret == 0 and (("virt-who.py -b -d" in output) or ("virtwho.py -b -d" in output)):
                    logger.info("Succeeded to check virt-who process.")
                else:
                    logger.error("Failed to check virt-who process.")
                    self.assert_(False, case_name)
                # (1) start a guest    
                self.vw_start_guests(guest_name)
                # check if the uuid is correctly monitored by virt-who.
                self.vw_check_uuid(guestuuid, uuidexists=True)
                # (2)pause a guest
                self.pause_vm(guest_name)
                # check if the uuid is correctly monitored by virt-who.
                self.vw_check_uuid(guestuuid, uuidexists=True)
                # (3)resume a guest
                self.resume_vm(guest_name)
                # check if the uuid is correctly monitored by virt-who.
                self.vw_check_uuid(guestuuid, uuidexists=True)
                # (4)shutdown a guest
                self.shutdown_vm(guest_name)
                # check if the uuid is correctly monitored by virt-who.
                #self.vw_check_uuid("", uuidexists=True)
                self.vw_check_uuid(guestuuid, uuidexists=True)
            else:
                raise FailException("Failed to run virt-who -b -d.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_stop_guests(guest_name)
            #stop virt-who command line mode
            self.vw_restart_virtwho()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
