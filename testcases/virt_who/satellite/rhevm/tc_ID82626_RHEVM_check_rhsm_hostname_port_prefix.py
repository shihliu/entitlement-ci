from utils import *
# from testcases.virt_who_polarion.vdsmbase import VDSMBase
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException

class tc_ID82626_RHEVM_check_rhsm_hostname_port_prefix(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            server_port = "443"
            server_prefix = "/rhsm"
            self.runcmd_service("stop_virtwho")

            # (1) Check config rhsm_hostname without "http://"
            # (1.1) Unregister host and disable rhevm mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_RHEVM")
            self.sub_unregister()
            # (1.2) Virt-who send host/guest mapping info to server
            self.config_hostname_port_prefix_disable(server_hostname, server_port, server_prefix)
            self.set_rhsm_hostname_prefix_port("rhevm", server_user, server_pass, server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()

            # (2) Check config rhsm_hostname with "http://"
            # (2.1) Virt-who send host/guest mapping info to server
            self.unset_all_virtwho_d_conf()
            self.set_rhsm_hostname_prefix_port("rhevm", server_user, server_pass, "http://" + server_hostname ,server_port, server_prefix)
            self.vw_check_mapping_info_number_in_rhsm_log()
            
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # Remove all conf in /etc/virt-who.d and reconfig virt-who, restart virt-who
            self.unset_all_virtwho_d_conf()
            self.set_rhevm_conf()
            self.runcmd_service("restart_virtwho")
            # Register host
            self.config_hostname_port_prefix_enable(server_hostname, server_port, server_prefix)
            self.sub_register(server_user, server_pass)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
