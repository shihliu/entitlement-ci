"""******************************************

@author        : shihliu@redhat.com
@date        : 2013-03-11

******************************************"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID183423_list_all_product(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            productid = self.get_rhsm_cons("productid")
            # list all available entitlement pools
            self.sub_listallavailpools(productid)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_enddate(self, output):
        datalines = output.splitlines()
        segs = []
        timeline = ""
        for line in datalines:
            if "Ends:" in line:
                 tmpline = line
                 segs.append(tmpline)
        for aa in segs:
            endtimeitem = aa.split(":")[0].replace(' ', '')
            endtimevalue = aa.split(":")[1].strip()
            if compare_time(endtimevalue) == 0:
                logger.info("It's correct to list this subscription.")    
            else :
                raise FailException("The subscription shouldn't be list")

    def compare_time(self, realenddate):
        systimebef = time.strftime('%y%m%d', time.localtime(time.time()))
        systemtime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(systimebef, "%y%m%d")))
        realendtime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(realenddate, "%m/%d/%Y")))
        delday = (realendtime - systemtime).days
        if delday > 0:
            logger.info("The subscription's end time after the system time")
            return 0
        else:
            raise FailException("The subscription's end time before the system time")

if __name__ == "__main__":
    unittest.main()
