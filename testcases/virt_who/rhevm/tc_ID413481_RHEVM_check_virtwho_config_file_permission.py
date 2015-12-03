from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID413481_RHEVM_check_virtwho_config_file_permission(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            virtwho_conf_file = '/etc/sysconfig/virt-who'

            cmd = "ls -alt %s" % virtwho_conf_file 
            ret, output = self.runcmd(cmd, "run cmd: %s" % cmd)
            if ret == 0 and output is not None:
                if output.strip().split()[0].strip() == "-rw-------.":
                    logger.info("Succeeded to check the virt-who config file's permission.")
                else:
                    raise FailException("Failed to check the virt-who config file's permission.")
            else:
                raise FailException("Failed to run: %s." % cmd)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
