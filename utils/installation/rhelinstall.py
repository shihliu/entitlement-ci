from utils.constants import RHEL_INSTALLATION_CONF
from utils.installation.install import Install
from utils.tools.shell.virshcommand import VirshCommand
from utils.tools.shell.samcommand import SAMCommand

class RHELInstall(Install):
    '''
    classdocs
    '''
    conf_file_name = RHEL_INSTALLATION_CONF
    target_ip = ""

    def install_host(self):
        pass

    def install_guest(self, guest_name):
        pass

    def install_product(self, sam_compose):
        pass

if __name__ == "__main__":
    RHELInstall().start()
