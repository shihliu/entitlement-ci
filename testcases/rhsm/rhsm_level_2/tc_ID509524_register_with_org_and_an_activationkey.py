"""
@author        : qianzhan@redhat.com
@date        : 2016-05-26
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509524_register_with_org_and_an_activationkey(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            orgname=self.get_rhsm_cons("default_org")
            serverip = get_exported_param("SERVER_IP")
            pro_name = self.get_rhsm_cons("productid")
            if self.test_server != "STAGE":
                # Make sure activationkey exists.
                if not self.sam_remote_activationkey_exist(serverip, orgname):
                    # Create activationkey
                    self.sam_remote_activationkey_creation(serverip, orgname)

                # Make sure activationkey attached pool
                poolid = self.sam_remote_fetch_pool(serverip,orgname)
                if not self.sam_remote_activationkey_check_pool(serverip, orgname, poolid):
                    self.sam_remote_activationkey_attach_pool(serverip, orgname, poolid)

            # Register with activationkey
            cmd = "subscription-manager register --org=%s --activationkey=qq"%orgname
            (ret, output) = self.runcmd(cmd, "register with activationkey")
            if ret == 0 and self.sub_isconsumed(pro_name):
                logger.info("It's successful to register with activationkey")
            else:
                raise FailException("Test Failed - Failed to register with activationkey")

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
