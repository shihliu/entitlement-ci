from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID1034_start_vw_service_by_ssh(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            ssh_cmd = "ssh %s %s; echo $?" % (get_exported_param("REMOTE_IP"), self.get_service_cmd("restart_virtwho"))
            ret, output = self.runcmd_local_pexpect(ssh_cmd)
            if output.strip() == "0" or "0" in output.strip():
                logger.info("Succeeded to run virt-who restart by ssh")
            else:
                raise FailException("Failed to run virt-who restart by ssh")
            ssh_cmd = "ssh %s %s" % (get_exported_param("REMOTE_IP"), self.get_service_cmd("status_virtwho"))
            ret, output = self.runcmd_local_pexpect(ssh_cmd)
            if "running" in output:
                logger.info("Succeeded to run virt-who status by ssh")
            else:
                raise FailException("Failed to run virt-who status by ssh")
            self.assert_(True, case_name)
        except Exception, SkipTest:
            logger.info(str(SkipTest))
            raise SkipTest
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
