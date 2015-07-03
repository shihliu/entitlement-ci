from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID202207_validate_default_config(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # (1) set virt-who config to default 
            ''' update virt-who configure to default '''
            cmd = "sed -i -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=0/g' /etc/sysconfig/virt-who"
            ret, output = self.runcmd(cmd, "updating virt-who configure file")
            if ret == 0:
                logger.info("Succeeded to update virt-who configure to default.")
            else:
                raise FailException("Failed to update virt-who configure to default.")
            # (2) check if the uuid is correctly monitored by virt-who.
            self.vw_restart_virtwho()
            self.vw_check_uuid(guestuuid, uuidexists=True)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.update_vw_configure()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
