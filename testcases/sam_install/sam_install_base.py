from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class SAM_Install_Base(unittest.TestCase):


    def runcmd(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None):
        if targetmachine_ip != None and targetmachine_ip != "":
            commander = Command(targetmachine_ip, targetmachine_user, targetmachine_pass)
        else:
            commander = Command(get_exported_param("REMOTE_IP"), username=get_exported_param("REMOTE_USER"), password=get_exported_param("REMOTE_PASSWD"))
        return commander.run(cmd, timeout, cmddesc)

    def install_sam(self, compose, server_ip=None, server_user=None, server_passwd=None):
        self.__stop_iptables(server_ip, server_user, server_passwd)
        self.__set_selinux(server_ip, server_user, server_passwd)
        self.__auto_subscribe(server_ip, server_user, server_passwd)
        self.__add_sam_repo(compose, server_ip, server_user, server_passwd)
        self.__install_katello(server_ip, server_user, server_passwd)
        self.__deploy_sam(server_ip, server_user, server_passwd)
        self.__import_manifest(server_ip, server_user, server_passwd)

    def __stop_iptables(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "service iptables stop"
        self.runcmd(cmd, "", server_ip, server_user, server_passwd)
        cmd = "chkconfig iptables off"
        self.runcmd(cmd, "", server_ip, server_user, server_passwd)
        cmd = "service iptables save"
        self.runcmd(cmd, "", server_ip, server_user, server_passwd)

    def __set_selinux(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "setenforce 0"
        self.runcmd(cmd, "", server_ip, server_user, server_passwd)
        cmd = "sed -i -e 's/SELINUX=.*/SELINUX=%s/g' /etc/sysconfig/selinux" % ("permissive")
        self.runcmd(cmd, "", server_ip, server_user, server_passwd)

    def __auto_subscribe(self, server_ip=None, server_user=None, server_passwd=None):
#         too slow for local install, add rhel repo instead
        cmd = "subscription-manager register --username=qa@redhat.com --password=uBLybd5JSmkRHebA --auto-attach"
        self.runcmd(cmd, "", server_ip, server_user, server_passwd)
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
        self.runcmd(cmd)

    def __add_sam_repo(self, sam_compose, server_ip=None, server_user=None, server_passwd=None):
        cmd = ('cat <<EOF > /etc/yum.repos.d/sam.repo\n'
            '[sam]\n'
            'name=sam\n'
            'baseurl=http://download.devel.redhat.com/devel/candidate-trees/SAM/%s/compose/SAM/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % sam_compose
            )
        self.runcmd(cmd, "", server_ip, server_user, server_passwd)

    def __install_katello(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "yum install -y katello-headpin-all"
        # cmd = "yum install -y git"
        self.runcmd(cmd, "", server_ip, server_user, server_passwd, timeout=7200)

    def __deploy_sam(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "katello-configure --deployment=sam --user-pass=admin"
        self.runcmd(cmd, "", server_ip, server_user, server_passwd, timeout=1800)

    def __import_manifest(self, server_ip=None, server_user=None, server_passwd=None):
        # only support remote run
        self.__upload_manifest()
        cmd = "headpin -u admin -p admin provider import_manifest --org=ACME_Corporation --name='Red Hat' --file=/root/sam_install_manifest.zip"
        self.runcmd(cmd, "", server_ip, server_user, server_passwd)

    def __upload_manifest(self, server_ip=None, server_user=None, server_passwd=None):
        # self.remote_put(sam_manifest, "/root/%s" % manifest_name)
        cmd = "wget http://10.66.100.116/projects/sam-virtwho/latest-manifest/sam_install_manifest.zip -P /root/"
        self.runcmd(cmd, "", server_ip, server_user, server_passwd)
