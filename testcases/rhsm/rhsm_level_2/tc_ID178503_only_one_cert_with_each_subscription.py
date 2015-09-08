"""
@author        : qianzhan@redhat.com
@date        : 2013-03-12
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import random

class tc_ID178503_only_one_cert_with_each_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # list availalbe entitlement pools
            productid = RHSMConstants().get_constant("productid")
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
            # get the number of entitlement cert
            cmd = "ls /etc/pki/entitlement | grep -v key.pem | wc -l"
            (ret, number) = self.runcmd(cmd, "get the number of entitlement cert")
            if (ret == 0) and (number.strip('\n') == "1"):
                logger.info("It's successful to verify that only one entitlement certificate is produced for each subscription to an entitlement pool")
            else:
                raise FailException("Test Failed - Failed to verify that only one entitlement certificate is produced for each subscription to an entitlement pool")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()


