from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID331776_bind_not_specify_quantity_auto_use_max_quantity_for_instance_based(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # make sure the system is physical machine
            is_physical = self.check_physical_machine()
            print "is_physical: ", is_physical
            if is_physical == False:
                self.virt_to_phy()

            # list an instance-based subscription pool
            cmd = 'subscription-manager list --available | egrep "Subscription Name:|Pool ID:|Suggested:"| grep "Red Hat Enterprise Linux High Touch Beta" -A2 '
            (ret, output) = self.runcmd(cmd, "list an instance-based subscription and get it's pool and suggested quantities.")
            if ret == 0 and output != '':
                poolid = output.split("\n")[1].split(":")[1].strip()
                suggested = output.split("\n")[2].split(":")[1].strip()
                logger.info("It's successful to list an instance-based subscription and get it's pool and suggested quantities..") 
            else:
                raise FailException("Test Failed - Failed to list an instance-based subscription and get it's pool and suggested quantities..")

            # attach an instance-based subscription without specifying the quantity.
            cmd = "subscription-manager attach --pool=%s" % poolid
            (ret, output) = self.runcmd(cmd, "attach an instance-based subscription")
            if ret == 0:
                logger.info("It's successful to attach an instance-based subscriptions without specifying quantity.") 
            else:
                raise FailException("Test Failed - Failed to attach an instance-based subscriptions without specifying quantity.")

            # check the attached quantities and suggested quantities.
            cmd = "subscription-manager list --consumed| grep Quantity"
            (ret, output) = self.runcmd(cmd, "check the attached quantities")
            attached = output.split(":")[1].strip()
            if ret == 0 and suggested == attached:
                logger.info("It's successful to attach an instance-based subscriptions without specifying quantity.") 
            else:
                raise FailException("Test Failed - Failed to attach an instance-based subscriptions without specifying quantity.")
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)
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
