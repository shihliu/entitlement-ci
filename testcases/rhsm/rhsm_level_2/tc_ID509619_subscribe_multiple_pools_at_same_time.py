from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509585_autoattach_with_single_SLA(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            pools=self.sub_list_availablepool_list()
            if len(pools)<1:
                logger.info('Available pools is less than 2, can not test this case.')
            else:
                cmd="subscription-manager attach --pool %s %s"%(pools[0],pools[1])
                (ret, output) = self.runcmd(cmd, "attach pools at same time")
                if ret != 0 and 'cannot parse argument:' in output:
                    logger.info("It's successful to check attaching multiple pools at same time")
                else:
                    raise FailException("Test Failed - Failed to check attaching multiple pools at same time")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
