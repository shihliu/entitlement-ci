from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID322862_VDSM_validate_unregister_check_output(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
            rhsmlogpath = '/var/log/rhsm/rhsm.log'
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = self.get_vw_cons("RHEVM_HOST")
            self.rhevm_start_vm(guest_name, rhevm_ip)

            # Modify the virt-who refresh interval
            cmd = "sed -i 's/#VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=100/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "changing interval to 100s in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to set VIRTWHO_INTERVAL=100.")
            else:
                raise FailException("Failed to set VIRTWHO_INTERVAL=100.")
            # restart virtwho service
            self.service_command("restart_virtwho")
            # unregister hosts
            self.sub_unregister()
            # check virt-who log
            cmd = "tail -200 %s " % rhsmlogpath
            ret, output = self.runcmd(cmd, "check output in rhsm.log")
            if ret == 0:
                if ("raise Disconnected" not in output) and ("Error while checking server version" not in output) and ("Connection refused" not in output) and ("Exception:" not in output):
                    logger.info("Success to check virt-who log normally after unregister system.")
                else:
                    raise FailException("Failed to check virt-who log normally after unregister system.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_register(SERVER_USER, SERVER_PASS)
            # move VIRTWHO_INTERVAL to default
            cmd = "sed -i 's/.*VIRTWHO_INTERVAL=.*/#VIRTWHO_INTERVAL=0/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(cmd, "move interval to default in virt-who config file")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)
            self.rhevm_stop_vm(guest_name, rhevm_ip)
if __name__ == "__main__":
    unittest.main()
