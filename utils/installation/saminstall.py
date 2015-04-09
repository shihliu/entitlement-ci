from utils.constants import SAM_INSTALLATION_CONF
from utils.installation.install import Install
from utils.tools.shell.virshcommand import VirshCommand
from utils.tools.shell.samcommand import SAMCommand

class SAMInstall(Install):
    '''
    classdocs
    '''
    conf_file_name = SAM_INSTALLATION_CONF
    target_ip = ""

    def install_host(self):
        pass

    def install_guest(self, guest_name):
        remote_ip = self.confs._confs["installation_host_ip"]
        username = self.confs._confs["host_username"]
        password = self.confs._confs["host_password"]
        # virsh_command = VirshCommand(remote_ip, username, password)
        virsh_command = VirshCommand(remote_ip, username, password)
        self.target_ip = virsh_command.create_vm("AUTO-%s" % guest_name)

    def find_guest(self, guest_name):
        remote_ip = self.confs._confs["installation_host_ip"]
        username = self.confs._confs["host_username"]
        password = self.confs._confs["host_password"]
        # virsh_command = VirshCommand(remote_ip, username, password)
        virsh_command = VirshCommand(remote_ip, username, password)
        self.target_ip = virsh_command.find_vm("AUTO-%s" % guest_name)

    def install_product(self, sam_compose):
        sam_command = SAMCommand(self.target_ip, "root", "redhat")
        sam_command.install_sam(sam_compose)

if __name__ == "__main__":
    SAMInstall().start()
