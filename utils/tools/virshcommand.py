'''
Use virsh API to manipulate vms
'''
from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class VirshCommand(Command):

    def create_vm(self, guest_name, guest_compose):
        self.__create_storage()
#         self.__unattended_install(guest_name, guest_compose)
#         return self.__check_vm_available(guest_name), "root", "redhat"
        # here user virt-clone to get a sam guest
        # you need to install a "RHEL6.6-Server-GA-AUTO" guest manually first
        # modify eth0, remove HWADDR and UUID, or else you will be failed to get dhcp IP
        self.clone_vm("RHEL6.6-Server-GA-BACKUP", guest_name)
        return self.start_vm(guest_name), "root", "redhat"

    def start_vm(self, guest_name):
        cmd = "virsh start %s" % (guest_name)
        self.run(cmd, timeout=None)
        return self.__check_vm_available(guest_name)

    def shutdown_vm(self, guest_name):
        cmd = "virsh shutdown %s" % (guest_name)
        self.run(cmd, timeout=None)
        time.sleep(180)

    def clone_vm(self, guest_name, cloned_guest_name):
        cmd = "virt-clone --original %s --name %s --file=/home/auto-imgs/%s.img" % (guest_name, cloned_guest_name, cloned_guest_name)
        self.run(cmd, timeout=None)

    def __unattended_install(self, guest_name, guest_compose):
        '''
        install a guest with virt-install command, need virt-install tool installed:
        can not quite normally, check ip to make sure guest installed temperatelly
        '''
        # self.__create_storage()
        # self.__create_img(guest_name)
        self.remote_put("/root/workspace/entitlement/data/kickstart/unattended/minimal.ks", "/root/minimal.ks")
        cmd = ('virt-install '
#                '--network=bridge:br0 '
               '--initrd-inject=/root/minimal.ks '
               '--extra-args "ks=file:/minimal.ks" '
               '--name=%s '
               '--disk path=/home/auto-imgs/%s.img,size=20 '
               '--ram 2048 '
               '--vcpus=1 '
               '--check-cpu '
               '--accelerate '
               '--hvm '
               '--location=%s '
#                 '--nographics '
               % (guest_name, guest_name, guest_compose))
#         from utils.tools.shell.remotesh import RemoteSH
#         RemoteSH.run_pexpect(cmd, self.remote_ip, "root", "redhat")
        self.run(cmd, timeout=600)
        time.sleep(120)

    def __check_vm_available(self, guest_name, timeout=600):
        terminate_time = time.time() + timeout
        while True:
            guestip = self.__mac_to_ip(self.__get_dom_mac_addr(guest_name))
            if guestip != "" and (not "can not get ip by mac" in guestip):
                return guestip
            if terminate_time < time.time():
                raise OSError("Process timeout has been reached")
            logger.debug("Check guest IP, wait 1 minute ...")
            time.sleep(60)

    def __get_dom_mac_addr(self, domname):
        """
        Get mac address of a domain
        Return mac address on SUCCESS or None on FAILURE
        """
        cmd = "virsh dumpxml " + domname + " | grep 'mac address' | awk -F'=' '{print $2}' | tr -d \"[\'/>]\""
        (ret, out) = self.run(cmd)
        if ret == 0:
            return out.strip("\n").strip(" ")
        else:
            return None

    def __mac_to_ip(self, mac):
        """
        Map mac address to ip, need nmap installed and ipget.sh in /root/ target machine
        Return None on FAILURE and the mac address on SUCCESS
        """
        if not mac:
            raise FailException("Failed to get guest mac ...")
        generate_ipget_cmd = "wget http://10.66.100.116/projects/sam-virtwho/latest-manifest/ipget.sh -P /root/ | chmod 777 /root/ipget.sh"
        self.run(generate_ipget_cmd)
        cmd = "sh /root/ipget.sh %s" % mac
        (ret, out) = self.run(cmd)
        return out.strip("\n").strip(" ")

    def __create_img(self, img_name, path="/home/auto-imgs/", size=20):
        cmd = "qemu-img create -f raw %s%s.img %sG" % (path, img_name, size)
        self.run(cmd, timeout=None)
 
    def __create_storage(self, path="/home/auto-imgs/"):
        cmd = "mkdir -p %s" % path
        self.run(cmd, timeout=None)

if __name__ == "__main__":
    virsh_command = VirshCommand()
    print virsh_command.create_vm("AUTO-SAM-1.4.0-RHEL-6-20140512.0")
