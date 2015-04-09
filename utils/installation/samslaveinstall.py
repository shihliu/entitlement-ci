from utils.tools.shell.virshcommand import VirshCommand
from utils.tools.shell.samcommand import SAMCommand

class SAMSlaveInstall():
    '''
    classdocs
    '''
    default_rhel_build = "http://download.englab.nay.redhat.com/pub/rhel/released/RHEL-6/6.6/Server/x86_64/os/"
    def install_host(self):
        pass

    def install_guest(self, guest_name, guest_compose=default_rhel_build):
        virsh_command = VirshCommand()
        guest_ip, guest_user, guest_passwd = virsh_command.create_vm(guest_name, guest_compose)
        return guest_ip, guest_user, guest_passwd

    def install_product(self, guest_ip, guest_user, guest_passwd, sam_compose):
        sam_command = SAMCommand(guest_ip, guest_user, guest_passwd)
        sam_command.install_sam(sam_compose)

    def clone_sam_guest(self, guest_name):
        virsh_command = VirshCommand()
        virsh_command.shutdown_vm(guest_name)
        virsh_command.clone_vm(guest_name, guest_name + "-virt-who")
        virsh_command.clone_vm(guest_name, guest_name + "-intergration")
        sam_virtwho_ip = virsh_command.start_vm(guest_name + "-virt-who")
        sam_intergration_ip = virsh_command.start_vm(guest_name + "-intergration")
        print sam_virtwho_ip, sam_intergration_ip

    def start(self, sam_compose="SAM-1.4.1-RHEL-6-20141009.0"):
        guest_ip, guest_user, guest_passwd = self.install_guest(sam_compose)
        self.install_product(guest_ip, guest_user, guest_passwd, sam_compose)
        self.clone_sam_guest(sam_compose)

if __name__ == "__main__":
#     SAMLocalInstall().start("SAM-1.4.1-RHEL-6-20141113.0")
    SAMSlaveInstall().start("SAM-1.4.1-RHEL-6-20141009.0") 
