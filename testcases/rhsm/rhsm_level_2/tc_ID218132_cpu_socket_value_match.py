from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID218132_cpu_socket_value_match(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            cmd = 'subscription-manager facts --list | grep "socket(s)"'
            (ret, output) = self.runcmd(cmd, "match socket(s)")
            if ret == 0 and 'cpu.cpu_socket(s)' in output and 'lscpu.socket(s)' in output:
                output_list = output.split("\n")
                for item in output_list:
                    if "cpu.cpu_socket(s)" in item:
                        socket1 = item.strip().split(":")[1]
                    elif 'lscpu.socket(s)' in item:
                        socket2 = item.strip().split(":")[1]
                if socket1 == socket2:
                    logger.info("Test Successful - It's successful checking cpu.cpu_socket(s) value match lscpu.cpu_socket(s) value in subscription-manager facts.") 
                else:
                    logger.info("Test skipped - The system facts doesn't have the lscpu.socket(s) option")
            else:
                raise FailException("Test Failed - Failed checking cpu.cpu_socket(s) value match lscpu.cpu_socket(s) value in subscription-manager facts.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
