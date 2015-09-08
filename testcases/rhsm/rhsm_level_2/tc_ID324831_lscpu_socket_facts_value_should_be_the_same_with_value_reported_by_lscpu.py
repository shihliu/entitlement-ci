from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID324831_lscpu_socket_facts_value_should_be_the_same_with_value_reported_by_lscpu(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # get lscpu.sockets fact value
            cmd = 'subscription-manager facts --list | grep "lscpu.socket(s)"'
            (ret, output) = self.runcmd(cmd, "list lscpu.sockets facts on ppc64")
            if ret == 0:
                lscpu_sockets_fact1 = output.split("\n")[0].split(":")[1].strip()
                logger.info("It's successful to get lscpu.sockets fact value")
            else:
                raise FailException("Test Failed - Failed to get lscpu.sockets fact value.")
            # get lscpu sockets value
            cmd = 'lscpu | grep Socket'
            (ret, output) = self.runcmd(cmd, "get lscpu sockets value on ppc64")
            if ret == 0:
                lscpu_sockets_value = output.split(':')[1].strip()
                logger.info("It's successful to get lscpu sockets value")
            else:
                raise FailException("Test Failed - Failed to get lscpu sockets value.")
            # compare the values
            if lscpu_sockets_fact1 == lscpu_sockets_value:
                logger.info("It's successful to check cpu_socket(s) facts value should be the same with value reported by lscpu on ppc64")
            else:
                raise FailException("Test Failed - Failed to check cpu_socket(s) facts value should be the same with value reported by lscpu on ppc64.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
