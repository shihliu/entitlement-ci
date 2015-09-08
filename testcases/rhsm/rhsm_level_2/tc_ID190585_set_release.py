from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import random

class tc_ID190585_set_release(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # list the subscription-manager release
            cmd = "subscription-manager release --list"
            (ret, output) = self.runcmd(cmd, "list release info")
            # 1. set list got from release list
            releaselist = RHSMConstants().get_constant("releaselist")
            outputtmp = output.strip().splitlines()
            if "+-" in outputtmp[0] and "+-" in outputtmp[2]:
                outputtmp.remove(outputtmp[0])
                outputtmp.remove(outputtmp[0])
                outputtmp.remove(outputtmp[0])
            # outputtmp = ','.join(output.strip().split('\n'))
            outputoneline = ','.join(outputtmp)
            print "outputoneline is %s" % outputoneline
            if ret == 0 and outputoneline == releaselist:
                # release_list = output.strip().splitlines()
                availrelease = random.sample(outputtmp, 1)[0]
                cmd = "subscription-manager release --set=%s" % (availrelease)
                (ret, output) = self.runcmd(cmd, "set a release from release list")
                if ret == 0 and "Release set to" in output:
                    logger.info("It's successful to set a release from release list")
                else:
                    raise FailException("Test Failed - Failed to set a release from release list")
            else: 
                raise FailException("Failed to check if release can be set correctly.")
            # 2. set invalid release 
            invalidrelease = 'abc'
            cmd = "subscription-manager release --set=%s" % (invalidrelease)
            (ret, output) = self.runcmd(cmd, "set a invalid release")
            if ret != 0 and "No releases match" in output:
                logger.info("It's successful to check if invalid release can be set.")
            else:
                raise FailException("Test Failed - Failed to check if invalid release can be set.")    
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
