from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class SAM_Install_Base(unittest.TestCase):

    def runcmd(self, cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None):
        if targetmachine_ip != None and targetmachine_ip != "":
            if targetmachine_user != None and targetmachine_user != "":
                commander = Command(targetmachine_ip, targetmachine_user, targetmachine_pass)
            else:
                commander = Command(targetmachine_ip, "root", "red2015")
        else:
            commander = Command(get_exported_param("REMOTE_IP"), "root", "red2015")
        return commander.run(cmd, timeout, cmddesc)

    def install_sam(self, compose, server_ip=None, server_user=None, server_passwd=None):
        self.__stop_iptables(server_ip, server_user, server_passwd)
        self.__set_selinux(server_ip, server_user, server_passwd)
        self.__set_hosts_file(server_ip, server_user, server_passwd)
        self.__auto_subscribe(server_ip, server_user, server_passwd)
        self.__add_sam_repo(compose, server_ip, server_user, server_passwd)
        self.__install_katello(server_ip, server_user, server_passwd)
        self.__deploy_sam(server_ip, server_user, server_passwd)
        self.__import_manifest(server_ip, server_user, server_passwd)

    def __stop_iptables(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "service iptables stop"
        ret, output = self.runcmd(cmd, "service iptables stop", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to run service iptables stop.")
        else:
            raise FailException("Test Failed - Failed to run service iptables stop.")
        cmd = "chkconfig iptables off"
        ret, output = self.runcmd(cmd, "chkconfig iptables off", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to run chkconfig iptables off.")
        else:
            raise FailException("Test Failed - Failed to run chkconfig iptables off.")
        cmd = "service iptables save"
        ret, output = self.runcmd(cmd, "service iptables save", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to run service iptables save.")
        else:
            raise FailException("Test Failed - Failed to run service iptables save.")

    def __set_selinux(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "setenforce 0"
        ret, output = self.runcmd(cmd, "setenforce 0", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to run setenforce 0.")
        else:
            raise FailException("Test Failed - Failed to run setenforce 0.")
        cmd = "sed -i -e 's/SELINUX=.*/SELINUX=%s/g' /etc/sysconfig/selinux" % ("permissive")
        ret, output = self.runcmd(cmd, "set /etc/sysconfig/selinux", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to set /etc/sysconfig/selinux.")
        else:
            raise FailException("Test Failed - Failed to set /etc/sysconfig/selinux.")

    def __set_hosts_file(self, server_ip=None, server_user=None, server_passwd=None):
        if server_ip != None and server_ip != "":
            cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (server_ip, server_ip, "samserv.redhat.com")
            ret, output = self.runcmd(cmd, "set /etc/hosts", server_ip, server_user, server_passwd)
            if ret == 0:
                logger.info("Succeeded to set /etc/hosts file.")
            else:
                raise FailException("Test Failed - Failed to set /etc/hosts file.")

    def __auto_subscribe(self, server_ip=None, server_user=None, server_passwd=None):
#         too slow for local install, add rhel repo instead
        cmd = "subscription-manager register --username=qa@redhat.com --password=uBLybd5JSmkRHebA --auto-attach"
        ret, output = self.runcmd(cmd, "auto attach", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to auto attach.")
        else:
            raise FailException("Test Failed - Failed to auto attach.")
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
        ret, output = self.runcmd(cmd, "add sam repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to add sam repo.")
        else:
            raise FailException("Test Failed - Failed to add sam repo.")

    def __install_katello(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "yum install -y katello-headpin-all"
        # cmd = "yum install -y git"
        ret, output = self.runcmd(cmd, "yum install -y katello-headpin-all && echo done", server_ip, server_user, server_passwd, timeout=3600)
        # here it always time out, need to research reason
#         if ret == 0:
#             logger.info("Succeeded to run yum install -y katello-headpin-all.")
#         else:
#             raise FailException("Test Failed - Failed to run yum install -y katello-headpin-all.")

    def __deploy_sam(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "katello-configure --deployment=sam --user-pass=admin"
        ret, output = self.runcmd(cmd, "katello-configure", server_ip, server_user, server_passwd, timeout=1800)
        if ret == 0:
            logger.info("Succeeded to run katello-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run katello-configure --deployment=sam --user-pass=admin.")

    def __import_manifest(self, server_ip=None, server_user=None, server_passwd=None):
        # only support remote run
        self.__upload_manifest(server_ip, server_user, server_passwd)
        cmd = "headpin -u admin -p admin provider import_manifest --org=ACME_Corporation --name='Red Hat' --file=/root/sam_install_manifest.zip"
        ret, output = self.runcmd(cmd, "import menifest", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to import menifest.")
        else:
            raise FailException("Test Failed - Failed to import menifest.")

    def __upload_manifest(self, server_ip=None, server_user=None, server_passwd=None):
        # self.remote_put(sam_manifest, "/root/%s" % manifest_name)
        cmd = "wget http://10.66.100.116/projects/sam-virtwho/latest-manifest/sam_install_manifest.zip -P /root/"
        ret, output = self.runcmd(cmd, "wget manifest to /root/", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to wget manifest to /root/.")
        else:
            raise FailException("Test Failed - Failed to wget manifest to /root/.")
