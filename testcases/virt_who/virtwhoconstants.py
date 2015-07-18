from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class VIRTWHOConstants(object):
    virt_who_cons = {
                    "KVM_GUEST_NAME":"6.5_Server_x86_64",

                    "beaker_image_server" : "10.16.96.131:/home/samdata",
#                     "local_image_path" : "/root/images",
                    "nfs_image_path" : "/root/images_nfs",
                    "local_mount_point" : "/tmp/images_mnt",

                    "esx_guest_url" : "http://10.66.100.116/projects/sam-virtwho/esx_guest/",

                    "SAM_USER":"admin",
                    "SAM_PASS":"admin",

                    "ESX_HOST":"10.66.128.77",
                    "ESX_GUEST_NAME":"ESX_7.1_Server_x86_64",

                    "VIRTWHO_ESX_OWNER" : "ACME_Corporation",
                    "VIRTWHO_ESX_ENV" : "Library",
                    "VIRTWHO_ESX_SERVER" : "10.66.78.89",
                    "VIRTWHO_ESX_USERNAME" : "administrator@vsphere.local",
                    "VIRTWHO_ESX_PASSWORD" : "qwer1234P!",


                    # limited subscription
                    "productid_guest" : "RH0604852",
                    "productname_guest" : "Red Hat Enterprise Linux Server for HPC Compute Node",
                    "guestlimit" : "1",
                    # unlimited subscription
                    "productid_unlimited_guest" : "RH00060",
                    "productname_unlimited_guest" : "Resilient Storage for Unlimited Guests",
                    "guestlimit_unlimited_guest" : "Unlimited",

                    # Datacenter subscription
                    "datacenter_name" : "Red Hat Enterprise Linux for Virtual Datacenters, Standard",
                    "datacenter_sku_id" : "RH00002",
                    "datacenter_bonus_sku_id" : "RH00050",
                    "datacenter_bonus_quantity" : "Unlimited",

                    # Datacenter subscription
                    "instancebase_name" : "Red Hat Enterprise Linux Server, Premium (Physical or Virtual Nodes)",
                    "instancebase_sku_id" : "RH00003",
                    }

    virt_who_commands = {
                    "restart_virtwho" : "service virt-who restart",
                    "restart_virtwho_7" : "systemctl restart  virt-who.service",
                    }

    def get_constant(self, name):
        return self.virt_who_cons[name]

    def get_command(self, command):
        if command + "-" + self.os_serial in self.virt_who_commands.keys():
            return self.virt_who_commands[command + "-" + self.os_serial]
        else:
            return self.virt_who_commands[command]

    def get_os_serials(self):
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
        (ret, output) = self.runcmd(cmd, showlogger=False)
        if ret == 0:
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Failed to get os serials")
