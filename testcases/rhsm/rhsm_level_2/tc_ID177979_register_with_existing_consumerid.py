"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID177979_register_with_existing_consumerid(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            
            consumer_certpath = '/etc/pki/consumer'
            entitlement_certpath = '/etc/pki/entitlement'
            # record consumerid
            consumerid = self.sub_get_consumerid()
            # autosubscribe
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # check certs the first time
            consumer1_cert_md5 = self.md5_value(consumer_certpath)
            entitlement1_cert_md5 = self.md5_value(entitlement_certpath)

            # clean the client data
            cmd = "subscription-manager clean"
            (ret, output) = self.runcmd(cmd, "run subscription-manager clean")
            if (ret == 0) and ("All local data removed" in output):
                logger.info("It's successful to run subscription-manager clean")
            else:
                raise FailException("Test Failed - error happened when run subscription-manager clean")
            # register with consumerid
            cmd = "subscription-manager register --username=%s --password=%s --consumerid=%s" % (username, password, consumerid)
            (ret, output) = self.runcmd(cmd, "register with existing consumerid")
            if (ret == 0) and ("The system has been registered with ID:" in output):
                logger.info("It's successful to register with existing consumerid")
            else:
                raise FailException("Test Failed - error happened when register with existing consumerid")

            # check certs the second time
            consumer2_cert_md5 = self.md5_value(consumer_certpath)
            entitlement2_cert_md5 = self.md5_value(entitlement_certpath)
            # compare certs md5sum
            if consumer1_cert_md5 == consumer2_cert_md5 and entitlement1_cert_md5 == entitlement2_cert_md5:
                logger.info("It's successful to check the consumer certs and entitlement certs")
            else:
                raise FailException("Test Failed - Failed to check the consumer certs and entitlement certs")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def md5_value(self, certpath):
        cmd = "md5sum `ls %s/*.pem`" % (certpath)
        (ret, output) = self.runcmd(cmd, "get md5sum value of cert files in %s " % certpath)
        if ret == 0 and output != None:
            logger.info("It's successful to get md5sum value of cert files in %s " % certpath)
            return output
        else:
            raise FailException("Test Failed - Failed to get md5sum value of cert files in %s " % certpath)

if __name__ == "__main__":
    unittest.main()






