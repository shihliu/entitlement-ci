from utils.tools.virshcommand import VirshCommand
from testcases.sam_install.sam_install_base import SAM_Install_Base

class SAM_LOCAL_INSTALL(SAM_Install_Base):
    '''
    classdocs
    '''
    default_rhel_build = "http://download.englab.nay.redhat.com/pub/rhel/released/RHEL-6/6.6/Server/x86_64/os/"
    default_sam_build = "http://download.devel.redhat.com/devel/candidate-trees/SAM/latest-SAM-1.4-RHEL-6/compose/SAM/x86_64/os/"
    def install_host(self):
        host_ip = "10.66.144.13"
        host_user = "root"
        host_passwd = "autosam"
        return host_ip, host_user, host_passwd

    def install_guest(self, host_ip, host_user, host_passwd, guest_name, guest_compose=default_rhel_build):
        virsh_command = VirshCommand(host_ip, host_user, host_passwd)
        guest_ip, guest_user, guest_passwd = virsh_command.create_vm(guest_name, guest_compose)
        return guest_ip, guest_user, guest_passwd

    def install_product(self):
        self.install_sam(self.default_sam_build)

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

if __name__ == "__main__":
    SAM_LOCAL_INSTALL().start("SAM-1.4.1-RHEL-6-20141009.0") 
