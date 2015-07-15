from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID202507_verify_virtwho_i(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            self.vw_stop_virtwho()

            cmd = "virt-who -i 5 -d"
            ret, output = self.runcmd(cmd, "run virt-who -i -d command")
            if ret == 0 :
                # check the status of virt-who
                cmd = "ps -ef | grep virt-who"
                ret, output = self.runcmd(cmd, "check the process of virt-who with background mode")
                if ret == 0 and (("virt-who.py -b -d" in output) or ("virtwho.py -b -d" in output)):
                    logger.info("Succeeded to check virt-who process.")
                else:
                    logger.error("Failed to check virt-who process.")
                    self.assert_(False, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            cmd = "sed -i 's/VIRTWHO_INTERVAL=5/#VIRTWHO_INTERVAL=0/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "restoring the interval time as default setting in virt-who config file")
            cmd = "rm /tmp/tail.rhsm.log"
            (ret, output) = self.runcmd(cmd, "remove /tmp/tail.rhsm.log file generated")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
