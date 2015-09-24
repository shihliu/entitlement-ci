from utils import *
from testcases.virt_who.esxbase import ESXBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID413481_ESX_check_virtwho_config_file_permission(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:

            # check the configure file's permission
            virtwho_conf='/etc/sysconfig/virt-who'
            cmd = "ls -lah %s; sleep 5" % virtwho_conf 
            ret, output = self.runcmd(cmd,"run cmd: %s" %cmd)
            if ret == 0 and output is not None:
                if  "-rw-------" in output:
                    logger.info("Succeeded to check the virt-who config file's permission.")
                else:
                    raise FailException("Failed to check the virt-who config file's permission.")
            else:
                raise FailException("Failed to run: %s." %cmd)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
