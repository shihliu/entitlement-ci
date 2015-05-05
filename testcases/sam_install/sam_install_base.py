from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class SAM_Install_Base(unittest.TestCase):

    commander = Command()

    def run(self, cmd, cmddesc=None, timeout=None):
        return self.commander.run(cmd, timeout, cmddesc)

    def install_sam(self, compose):
        self.__stop_iptables()
        self.__set_selinux()
        self.__auto_subscribe()
        self.__add_sam_repo(compose)
        self.__install_katello()
        self.__deploy_sam()
        self.__import_manifest()

    def __stop_iptables(self):
        cmd = "service iptables stop"
        self.run(cmd)
        cmd = "chkconfig iptables off"
        self.run(cmd)
        cmd = "service iptables save"
        self.run(cmd)

    def __set_selinux(self):
        cmd = "setenforce 0"
        self.run(cmd)
        cmd = "sed -i -e 's/SELINUX=.*/SELINUX=%s/g' /etc/sysconfig/selinux" % ("permissive")
        self.run(cmd)

    def __auto_subscribe(self):
#         too slow for local install, add rhel repo instead
        cmd = "subscription-manager register --username=qa@redhat.com --password=uBLybd5JSmkRHebA --auto-attach"
        self.run(cmd)
#         cmd = ('cat <<EOF > /etc/yum.repos.d/myrhel.repo\n'
#             '[rhel]\n'
#             'name=rhel\n'
#             'baseurl=http://download.englab.nay.redhat.com/pub/rhel/released/RHEL-6/6.6/Server/x86_64/os/\n'
#             'enabled=1\n'
#             'gpgcheck=0\n'
#             '[rhel-optional]\n'
#             'name=rhel-optional\n'
#             'baseurl=http://download.englab.nay.redhat.com/pub/rhel/released/RHEL-6/6.6/Server/optional/x86_64/os/\n'
#             'enabled=1\n'
#             'gpgcheck=0\n'
#             'EOF'
#             )
        self.run(cmd)

    def __add_sam_repo(self, sam_compose):
        cmd = ('cat <<EOF > /etc/yum.repos.d/sam.repo\n'
            '[sam]\n'
            'name=sam\n'
            'baseurl=http://download.devel.redhat.com/devel/candidate-trees/SAM/%s/compose/SAM/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % sam_compose
            )
        self.run(cmd)

    def __install_katello(self):
        cmd = "yum install -y katello-headpin-all"
        # cmd = "yum install -y git"
        self.run(cmd, timeout=7200)

    def __deploy_sam(self):
        cmd = "katello-configure --deployment=sam --user-pass=admin"
        self.run(cmd, timeout=1800)

    def __import_manifest(self):
        # only support remote run
        self.__upload_manifest()
        cmd = "headpin -u admin -p admin provider import_manifest --org=ACME_Corporation --name='Red Hat' --file=/root/sam_install_manifest.zip"
        self.run(cmd)

    def __upload_manifest(self):
        # self.remote_put(sam_manifest, "/root/%s" % manifest_name)
        cmd = "wget http://10.66.100.116/projects/sam-virtwho/latest-manifest/sam_install_manifest.zip -P /root/"
        self.run(cmd)