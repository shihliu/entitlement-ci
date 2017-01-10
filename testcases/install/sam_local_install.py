from utils import *
from utils.tools.shell.command import Command
from utils.tools.virshcommand import VirshCommand
from utils.exception.failexception import FailException
from testcases.install.install_base import Install_Base

class SAM_LOCAL_INSTALL(Install_Base):
    '''
    classdocs
    '''
    default_rhel_build = "http://download.englab.nay.redhat.com/pub/rhel/released/RHEL-6/6.6/Server/x86_64/os/"
    default_sam_build = "latest-SAM-1.4-RHEL-6"
    def install_host(self):
        host_ip = "10.66.144.13"
        host_user = "root"
        host_passwd = "red2015"
        return host_ip, host_user, host_passwd

    def install_guest(self, host_ip, host_user, host_passwd, guest_name, guest_compose=default_rhel_build):
        virsh_command = VirshCommand(host_ip, host_user, host_passwd)
        guest_ip, guest_user, guest_passwd = virsh_command.create_vm(guest_name, guest_compose)
        return guest_ip, guest_user, guest_passwd

    def install_product(self, guest_ip, guest_user, guest_passwd, compose):
        self.install_sam(compose, guest_ip, guest_user, guest_passwd)

    def clone_sam_guest(self, host_ip, host_user, host_passwd, guest_name):
        virsh_command = VirshCommand(host_ip, host_user, host_passwd)
        virsh_command.shutdown_vm(guest_name)
        virsh_command.clone_vm(guest_name, guest_name + "-virt-who")
        virsh_command.clone_vm(guest_name, guest_name + "-intergration")
        sam_virtwho_ip = virsh_command.start_vm(guest_name + "-virt-who")
        sam_intergration_ip = virsh_command.start_vm(guest_name + "-intergration")
        print sam_virtwho_ip, sam_intergration_ip

    def start(self, sam_compose):
        host_ip, host_user, host_passwd = self.install_host()
        guest_ip, guest_user, guest_passwd = self.install_guest(host_ip, host_user, host_passwd, sam_compose)
        self.install_product(guest_ip, guest_user, guest_passwd, sam_compose)
        self.clone_sam_guest(host_ip, host_user, host_passwd, sam_compose)

    def curl_sam_compose(self):
        cmd = "curl -s -k http://download.devel.redhat.com/devel/candidate-trees/SAM/latest-SAM-1.4-RHEL-6/COMPOSE_ID"
        ret, output = Command().run(cmd)
        if ret == 0:
            logger.info("Succeeded to get latest sam compose.")
            return output.strip()
        else:
            raise FailException("Test Failed - Failed to get latest sam compose.")

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            sam_compose = self.curl_sam_compose()
            self.start(sam_compose)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
