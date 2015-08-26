from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException

class VIRTWHOConstants(object):
    virt_who_cons = {
                    "KVM_GUEST_NAME":"6.7_Server_x86_64",

                    "beaker_image_server" : "10.16.96.131:/home/samdata",
                    "nfs_image_path" : "/root/images_nfs",
                    "local_mount_point" : "/tmp/images_mnt",

                    "esx_guest_url" : "http://10.66.100.116/projects/sam-virtwho/esx_guest/",

                    "SAM_USER":"admin",
                    "SAM_PASS":"admin",

                    "ESX_HOST":"10.66.128.10",
                    "ESX_GUEST_NAME":"ESX_7.1_Server_x86_64",
                    "VMWARE_CMD_IP":"10.66.78.89",

                    "VIRTWHO_ESX_OWNER" : "ACME_Corporation",
                    "VIRTWHO_ESX_ENV" : "Library",
                    "VIRTWHO_ESX_SERVER" : "10.66.78.89",
                    "VIRTWHO_ESX_USERNAME" : "administrator@vsphere.local",
                    "VIRTWHO_ESX_PASSWORD" : "qwer1234P!",

                    "VIRTWHO_LIBVIRT_OWNER" : "ACME_Corporation",
                    "VIRTWHO_LIBVIRT_ENV" : "Library",
                    "VIRTWHO_LIBVIRT_USERNAME" : "root",

                    # limited subscription
                    "productid_guest" : "RH0103708",
                    "productname_guest" : "Red Hat Enterprise Linux Server, Premium",
                    "guestlimit" : "4",
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
                    "restart_virtwho_systemd" : "systemctl restart virt-who.service",

                    "stop_virtwho" : "service virt-who stop",
                    "stop_virtwho_systemd" : "systemctl stop virt-who.service",

                    "status_virtwho" : "service status restart",
                    "status_virtwho_systemd" : "systemctl status virt-who.service",

                    "restart_libvirtd" : "service libvirtd restart",
                    "restart_libvirtd_systemd" : "systemctl restart libvirtd.service",

                    "restart_network" : "service network restart",
                    "restart_network_systemd" : "systemctl restart network",
                    }

    def get_constant(self, name):
        if name == "VIRTWHO_ESX_OWNER" and get_exported_param("SERVER_TYPE") == "SATELLITE":
            return "Default_Organization"
        else:
            return self.virt_who_cons[name]
