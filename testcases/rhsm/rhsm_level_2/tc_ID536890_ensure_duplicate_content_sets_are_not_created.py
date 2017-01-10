from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID536890_ensure_duplicate_content_sets_are_not_created(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        if self.test_server == "STAGE":
            try:
                # Register
                username = self.get_rhsm_cons("username_market")
                password = self.get_rhsm_cons("password_market")
                self.sub_register(username, password)
         
                # get available pool
                pools = self.sub_list_availablepool_list()

                # attach the firstpool
                self.attach_pool(pools[0])

                # yum repolist firsttime
                out1 = self.yum_repolist()

                # attach the second time
                self.attach_pool(pools[1])

                # yum repolist firsttime
                out2 = self.yum_repolist()

                if out1 == out2:
                    logger.info("It's successful to verify no duplicate repo")
                else:
                    raise FailException("Test Failed - Failed to verify no duplicate repo")

                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
            finally:
                self.restore_environment()
                logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def attach_pool(self, poolid):
        cmd = "subscription-manager attach --pool=%s"%poolid
        (ret, output) = self.runcmd(cmd, "attach pool")
        if ret == 0:
            logger.info("It's successful to attach pool")
        else:
            raise FailException("Test Failed - Failed to attach pool")

    def yum_repolist(self):
        cmd = "yum repolist"
        (ret, output) = self.runcmd(cmd, "attach pool")
        if ret == 0:
            return output
            logger.info("It's successful to attach pool")
        else:
            raise FailException("Test Failed - Failed to attach pool")

if __name__ == "__main__":
    unittest.main()
