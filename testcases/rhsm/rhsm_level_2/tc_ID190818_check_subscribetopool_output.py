from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException
import random

class tc_ID190818_check_subscribetopool_output(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            #list availalbe entitlement pools
            productid = self.get_rhsm_cons("productid")
            availpoollist = self.sub_listavailpools(productid)
            #get an available entitlement pool to subscribe with random.sample
            availpool = random.sample(availpoollist, 1)[0]
            if "SubscriptionName" in availpool:
                if "PoolId" in availpool:
                    poolid = availpool["PoolId"]
                    subscriptionname = availpool["SubscriptionName"]
                else:
                    poolid = availpool["PoolID"]
                    subscriptionname = availpool["SubscriptionName"]
            #subscribe the product with poolid
            cmd = "subscription-manager subscribe --pool=%s" %poolid
            (ret, output) = self.runcmd(cmd, "subscribe with poolid")
            expectout = "Successfully consumed a subscription for: %s" %subscriptionname
            expectoutnew = "Successfully attached a subscription for: %s" %subscriptionname
            if 0 == ret and (expectout in output or expectoutnew in output) :
                logger.info("It's Successfull to verify the output of cmd subscription-manager subscribe --pool=<poolid>!")
            else:
                raise FailException("Test Faild - Failed to verify the output of cmd subscription-manager subscribe --pool=<poolid>!")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
