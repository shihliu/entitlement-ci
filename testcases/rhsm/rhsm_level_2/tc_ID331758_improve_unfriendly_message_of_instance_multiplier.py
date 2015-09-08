from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID331758_improve_unfriendly_message_of_instance_multiplier(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            # make sure the system is physical machine
            is_physical = self.check_physical_machine()
            print "is_physical: ", is_physical
            if is_physical == False:
                self.virt_to_phy()
            # list an instance-based subscription pool
            cmd = 'subscription-manager list --available | egrep "Subscription Name:|Pool ID:|Suggested:"| grep "Red Hat Enterprise Linux High Touch Beta" -A2 | grep "Pool"'
            (ret, output) = self.runcmd(cmd, "list an instance-based subscription and get it's pool")
            if ret == 0 and output != '':
                poolid = output.split(":")[1].strip()
                logger.info("It's successful to list an instance-based subscription and get it's pool.") 
            else:
                raise FailException("Test Failed - Failed to list an instance-based subscription and get it's pool.")
            # attach an instance-based subscription with a quantity that is not an even multiple of the instance_multiplier
            cmd = "subscription-manager attach --pool=%s --quantity=1" % poolid
            (ret, output) = self.runcmd(cmd, "attach an instance-based subscription")
            if ret != 0 and "must be attached using a quantity evenly divisible by 2" in output:
                logger.info("It's successful to check the error message of instance multiplier.") 
            else:
                raise FailException("Test Failed - Failed to check the error message of instance multiplier.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if is_physical == False:
                self.phy_to_virt()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_physical_machine(self):
        is_physical = True
        cmd = "subscription-manager facts --list | grep virt.is_guest:"
        (ret, output) = self.runcmd(cmd, "check physical machine")
        if ret == 0 and output.split(':')[1].strip() == 'True':
            is_physical = False
        return is_physical

    def virt_to_phy(self):
        cmd = "echo '{\"virt.is_guest\": \"False\"}' > /etc/rhsm/facts/custom.facts; subscription-manager facts --update"
        (ret, output) = self.runcmd(cmd, "virt_to_phy")
        if ret == 0 and "Successfully updated the system facts" in output:
            logger.info("It's successful to virt_to_phy.") 
        else:
            raise FailException("Test Failed - Failed to virt_to_phy.")

    def phy_to_virt(self):
        cmd = "echo '{\"virt.is_guest\": \"True\"}' > /etc/rhsm/facts/custom.facts; subscription-manager facts --update"
        (ret, output) = self.runcmd(cmd, "phy_to_virt")
        if ret == 0 and "Successfully updated the system facts" in output:
            logger.info("It's successful to phy_to_virt.") 
        else:
            raise FailException("Test Failed - Failed to phy_to_virt.")

if __name__ == "__main__":
    unittest.main()
