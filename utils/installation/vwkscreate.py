from utils.constants import VIRTWHO_KICKSTART_CONF
from utils.installation.install import Install
from utils.tools.shell.virtwhokickstart import VirtWhoKickstart
from utils import logger

class VWKSCreate(Install):
    '''
    classdocs
    '''
    conf_file_name = VIRTWHO_KICKSTART_CONF
    target_ip = ""

    def install_host(self):
        pass

    def install_guest(self, guest_name):
        pass

    def install_product(self, sam_compose):
        pass

    def start(self):
        new, build = self.check_build()
        if new == -1:
            logger.info("No rhel new build available yet, just exit ...")
            return -1, build
        else:
            logger.info("Found rhel new build %s, begin creating virt-who kickstart file ..." % build)
            VirtWhoKickstart().create(build)
            return 0, build

if __name__ == "__main__":
    VirtWhoKickstart().create("RHEL5.11-Server-20140709.0")
