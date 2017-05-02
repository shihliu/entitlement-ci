from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID0000_template(VIRTWHOBase):
    def run_kvm(self):
        try:
            self.skipTest("test case skiped, not fit for kvm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_vdsm(self):
        try:
            self.skipTest("test case skiped, not fit for vdsm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_rhevm(self):
        try:
            self.skipTest("test case skiped, not fit for rhevm ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_hyperv(self):
        try:
            self.skipTest("test case skiped, not fit for hyperv ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_esx(self):
        try:
            self.skipTest("test case skiped, not fit for esx ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def run_xen(self):
        try:
            self.skipTest("test case skiped, not fit for xen ...")
        finally:
            logger.info("---------- succeed to restore environment ----------")

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            hypervisor_type = get_exported_param("HYPERVISOR_TYPE")
            if hasattr(self, "run_" + hypervisor_type):
                getattr(self, "run_" + hypervisor_type)()
            else:
                self.skipTest("test case skiped, not fit for %s" % hypervisor_type)
            self.assert_(True, case_name)
        except Exception, SkipTest:
            logger.info(str(SkipTest))
            raise SkipTest
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

# template for platform not related cases
# class tc_ID0000_template(VIRTWHOBase):
#     def test_run(self):
#         case_name = self.__class__.__name__
#         logger.info("========== Begin of Running Test Case %s ==========" % case_name)
#         try:
#             pass
#             self.assert_(True, case_name)
#         except Exception, SkipTest:
#             logger.info(str(SkipTest))
#             raise SkipTest
#         except Exception, e:
#             logger.error("Test Failed - ERROR Message:" + str(e))
#             self.assert_(False, case_name)
#         finally:
#             logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
