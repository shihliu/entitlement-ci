"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID180386_unsubscribe_using_cert_serialnumber(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
            #list consumed
            cmd_list="subscription-manager list --consumed | grep Serial"
            (ret,output)=self.runcmd(cmd_list,"list consumed subscription and record serial number")
            if ret == 0 and output!=None:
                serialnumber=output.strip().split(':')[1].strip()
                logger.info("It's successful to list consumed subscription and record serial number.")
            else:
                raise FailException("Test Failed - It's failed to list consumed subscription and record serial number.")
            #unsubscribe the consumed subscription via the serial number
            cmd_unsub="subscription-manager unsubscribe --serial=%s"%serialnumber
            (ret,output)=self.runcmd(cmd_unsub,"unsubscribe the consumed subscription via the serial number")
            if ret == 0 and output!=None:
                logger.info("It's successful to run unsubscribe via the serial number.")
            else:
                raise FailException("Test Failed - It's failed to unsubscribe the consumed subscription via the serial number.")
            #list consumed after unsubscribe the consumed subscription via the serial number
            cmd_list="subscription-manager list --consumed"
            (ret,output)=self.runcmd(cmd_list,"list consumed subscription")
            if ret == 0 and "No consumed subscription pools to list" in output:
                logger.info("It's successful to list consumed subscription")
            else:
                raise FailException("Test Failed - It's failed to list the consumed subscription.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
