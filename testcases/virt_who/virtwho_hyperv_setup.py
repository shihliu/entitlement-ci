from utils import *
from testcases.virt_who.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class virtwho_hyperv_setup(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
#             self.hyperv_run_cmd("getvm rhel7.2")
#             self.hyperv_run_cmd("get-vm rhel7.2|select *")
#             self.hyperv_run_cmd("start-vm rhel7.2 -asjob")
#             self.hyperv_run_cmd("start-vm rhel7.2")
#             self.hyperv_run_cmd("stop-vm rhel7.2")
            self.hyperv_run_cmd("(Get-VMNetworkAdapter -VMName rhel7.2).IpAddresses ")
#             self.hyperv_run_cmd("'get-vm | where { $_.state -eq 'running'} | get-vmnetworkadapter | Select VMName,@{Name="IP";Expression={$_.IPAddresses | where {$_ -match "^172\."}}} | Sort VMName'")
 
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()