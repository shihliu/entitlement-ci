from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException
import random

class tc_ID115174_subscribetopool(RHSMBase):
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
                if availpool.has_key("PoolID"):
                    poolid = availpool["PoolID"]
                else:
                    poolid = availpool["PoolId"]
                subscriptionname = availpool["SubscriptionName"]
                productid = availpool["SKU"]
                # subscribe the product with poolid
                cmd = "subscription-manager subscribe --pool=%s" % poolid
                (ret, output) = self.runcmd(cmd, "subscribe with poolid")
                expectout = "Successfully consumed a subscription for: %s" % subscriptionname
                # expectoutnew is for rhel new feature output
                expectoutnew = "Successfully attached a subscription for: %s" % subscriptionname
                if 0 == ret and ((expectout in output) or (expectoutnew in output)):
                    # check whether entitlement certificates generated and productid in them or not
                    self.sub_checkentitlementcerts(productid)
                    logger.info("It's successful to do subscribe to a pool")
                else:
                    logger.error("Test Failed - error happened when do subscribe to a pool")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()








		
