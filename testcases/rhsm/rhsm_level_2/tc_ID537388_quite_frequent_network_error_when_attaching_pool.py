from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID537388_quite_frequent_network_error_when_attaching_pool(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            #get a pool to attach
            pool_to_attach = self.sub_list_availablepool_list()[0]

            # attaching pool frequently
            cmd="i=0; while [ $i -lt 4 ]; do subscription-manager register --force --username=%s --password=%s && subscription-manager attach --pool=%s && subscription-manager unregister || break; i=$[$i+1]; done"%(username, password, pool_to_attach)
            (ret,output)=self.runcmd(cmd,"attach pool frequently")
            if ret == 0 and ('Network error' not in output):
                logger.info("It's successful to verify that no network error when attaching pool frequently")
            else:
                raise FailException("Test Failed - Failed to verify that no network error when attaching pool frequently")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
