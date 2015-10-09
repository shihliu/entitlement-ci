"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException
import random

class tc_ID178500_bind_and_unbind_action_in_syslog(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # list availalbe entitlement pools
            productid = self.get_rhsm_cons("productid")
            availpoollist = self.sub_listavailpools(productid)

            # get an available entitlement pool to subscribe with random.sample
            availpool = random.sample(availpoollist, 1)[0] 
            if "SubscriptionName" in availpool:
                poolid = availpool["PoolID"]
                subscriptionname = availpool["SubscriptionName"]
                productid = availpool["SKU"]

            # subscribe the product with poolid
            cmd = "subscription-manager subscribe --pool=%s" % poolid
            (ret, output) = self.runcmd(cmd, "subscribe with poolid")
            expectout = "Successfully consumed a subscription for: %s" % subscriptionname
            # expectoutnew is for rhel new feature output
            expectoutnew = "Successfully attached a subscription for: %s" % subscriptionname
            if 0 == ret and ((expectout in output) or (expectoutnew in output)):
                logger.info("It's successful to do subscribe to a pool")
            else:
                logger.error("Test Failed - error happened when do subscribe to a pool")

            # get the entitlement cert name
            #cmd = "ls /etc/pki/entitlement/*.pem | grep -v key.pem"
            #(ret, certname0) = self.runcmd(cmd, "get the entitlement cert name")
            #if (ret == 0) and (certname0 != None):
            #    logger.info("It's successful to get the entitlement cert name")
            #    certname = certname0.strip('\n')
            #else:
            #    raise FailException("Test Failed - Failed to get the entitlement cert name")

            # not entitlement cert but serial number in rhsm.log for new rhel
            # get serial number from consumed subscription
            serial = self.get_subscription_serialnumlist()[0]
            # check the syslog for subscribe info
            cmd = "tail -100 /var/log/rhsm/rhsm.log | grep Deleted -B10 |grep Added -A10 | grep '%s'" % serial
            (ret, loginfo) = self.runcmd(cmd, "check the syslog for subscribe info")
            if ret == 0 and loginfo != None:
                logger.info("It's successful to check the syslog for subscribe info")
            else:
                raise FailException("Test Failed - Failed to check the syslog for subscribe info")

            # unsubscribe
            self.sub_unsubscribe()

            # check the syslog for unsubscribe info
            cmd = "tail -100 /var/log/rhsm/rhsm.log | grep Deleted -A10 | grep '%s'" % serial
            (ret, loginfo) = self.runcmd(cmd, "check the syslog for subscribe info")
            if ret == 0 and loginfo != None:
                logger.info("It's successful to check the syslog for unsubscribe info")
            else:
                raise FailException("Test Failed - Failed to check the syslog for unsubscribe info")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
