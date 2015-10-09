from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException
import random

class tc_ID115187_updatefactsinfo(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            org_cpusocket = self.get_current_facts_info()
            selectlist = ['1', '2', '3', '4', '5', '6', '7', '8']
            if org_cpusocket in selectlist:
                selectlist.remove(org_cpusocket)
                modified_cpusockets = random.sample(selectlist, 1)[0]
            # update facts info of the system
            self.update_current_facts_info(org_cpusocket, modified_cpusockets)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def get_current_facts_info(self):
        cmd = "cat /var/lib/rhsm/facts/facts.json |sed -e 's/[{}]/''/g' | awk -v k=\"text\" '{n=split($0,a,\",\"); for (i=1; i<=n; i++) print a[i]}'|grep '\"cpu.cpu_socket(s)\"'|tr -cd 0-9 && echo"
        (ret, output) = self.runcmd(cmd, "get current facts")	
        logger.info("current cpu_socket facts of the system: %s" % output)
        if ret == 0:
            return output[-2]
        else:
            raise FailException("Test Failed - Failed to get current facts of cpu_socket.")

    def update_current_facts_info(self, org_cpusocket, modified_cpusockets):
        # generate custom facts
        cmd = """echo '{"cpu.cpu_socket(s)":%s}' > /etc/rhsm/facts/custom.facts""" % modified_cpusockets
        (ret, output) = self.runcmd(cmd, "generate custom facts")
        # update facts of cpu.cpu_sockets
        cmd = "subscription-manager facts --update"
        (ret, output) = self.runcmd(cmd, "update custom facts")
        if ret == 0 and "Successfully updated the system facts" in output:
            if self.is_current_facts_updated(org_cpusocket, modified_cpusockets):
                logger.info("It's successful to update the system facts.")
            else:
                raise FailException("Test Failed - Failed to update the system facts.")
        else:
            raise FailException("Test Failed - Failed to update the system facts.")

    def is_current_facts_updated(self, orgvalue, modifiedvalue):
        flag = False
        currentvalue = self.get_current_facts_info()
        if currentvalue == modifiedvalue and currentvalue != orgvalue:
            flag = True
        return flag

if __name__ == "__main__":
    unittest.main()















