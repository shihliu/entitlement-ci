class VIRTWHOConstants(object):
    virtwho_cons = {
    # for kvm
    "KVM_GUEST_NAME":                   "6.7_Server_x86_64",
    "beaker_image_server":              "10.16.96.131:/home/samdata",
    "nfs_image_path":                   "/root/images_nfs",
    "local_mount_point":                "/tmp/images_mnt",

    # for esx
    "esx_guest_url":                    "http://10.66.100.116/projects/sam-virtwho/esx_guest/",
    "ESX_HOST":                         "10.66.128.10",
    "ESX_GUEST_NAME":                   "ESX_7.1_Server_x86_64",
    "VMWARE_CMD_IP":                    "10.66.78.89",
    "VIRTWHO_ESX_OWNER":                "ACME_Corporation",
    "VIRTWHO_ESX_ENV":                  "Library",
    "VIRTWHO_ESX_SERVER":               "10.66.79.5",
    "VIRTWHO_ESX_USERNAME":             "administrator@vsphere.local",
    "VIRTWHO_ESX_PASSWORD":             "qwer1234P!",

    # for rhevm
#    "NFSserver_ip":                     "10.16.96.131",
    "NFSserver_ip":                     "10.66.129.9",
    "proxy_ip":                         "proxy=https:\/\/squid.corp.redhat.com:3128",
#     "nfs_dir_for_storage":              "/home/NFS2",
#     "nfs_dir_for_export":               "/home/NFS3",
    "nfs_dir_for_storage":              "/home/data2",
    "nfs_dir_for_export":               "/home/export",
    "RHEVM_HOST":                       "10.66.79.23",
    "RHEL_RHEVM_GUEST_NAME":            "6.7_Server_x86_64",
    "NFSserver_ip_test":                "10.66.129.9",
    "NFS_DIR_FOR_storage":              "/home/data2",
    "NFS_DIR_FOR_export":               "/home/export",
#     "NFS_DIR_FOR_storage":              "/home/NFS2",
#     "NFS_DIR_FOR_export":               "/home/NFS3",
    "VIRTWHO_RHEVM_OWNER":              "ACME_Corporation",
    "VIRTWHO_RHEVM_ENV":                "Library",
    "VIRTWHO_RHEVM_SERVER ":            "10.66.79.83",
    "VIRTWHO_RHEVM_USERNAME":           "admin@internal",
    "VIRTWHO_RHEVM_PASSWORD":           "redhat",
    "VIRTWHO_LIBVIRT_OWNER":            "ACME_Corporation",
    "VIRTWHO_LIBVIRT_ENV":              "Library",
    "VIRTWHO_LIBVIRT_USERNAME":         "root",

    # limited subscription
    "productid_guest":                  "RH0103708",
    "productname_guest":                "Red Hat Enterprise Linux Server, Premium",
    "guestlimit":                       "4",
    # unlimited subscription
    "productid_unlimited_guest":        "RH00060",
    "productname_unlimited_guest":      "Resilient Storage for Unlimited Guests",
    "guestlimit_unlimited_guest":       "Unlimited",
    # Datacenter subscription
    "datacenter_name":                  "Red Hat Enterprise Linux for Virtual Datacenters, Standard",
    "datacenter_sku_id":                "RH00002",
    "datacenter_bonus_sku_id":          "RH00050",
    "datacenter_bonus_quantity":        "Unlimited",
    # Datacenter subscription
    "instancebase_name":                "Red Hat Enterprise Linux Server, Premium (Physical or Virtual Nodes)",
    "instancebase_sku_id":              "RH00003",
    }

    sam_cons = {
    "username":                         "admin",
    "password":                         "admin",
    }

    satellite_cons = {
    "username":                         "admin",
    "password":                         "admin",
    }

    stage_cons = {
    "username":                         "stage_virtwho_test",
    "password":                         "redhat",
    }

    virt_who_commands = {
    "restart_virtwho":                  "service virt-who restart",
    "restart_virtwho_systemd":          "systemctl restart virt-who.service",
    
    "stop_virtwho":                     "service virt-who stop",
    "stop_virtwho_systemd":             "systemctl stop virt-who.service",
    
    "status_virtwho":                   "service status restart",
    "status_virtwho_systemd":           "systemctl status virt-who.service",
    
    "restart_libvirtd":                 "service libvirtd restart",
    "restart_libvirtd_systemd":         "systemctl restart libvirtd.service",
    
    "restart_network":                  "service network restart",
    "restart_network_systemd":          "systemctl restart network",
    }

    virtwho_sam_cons = dict(virtwho_cons.items() + sam_cons.items())
    virtwho_satellite_cons = dict(virtwho_cons.items() + satellite_cons.items())
    virtwho_stage_cons = dict(virtwho_cons.items() + stage_cons.items())

    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(VIRTWHOConstants, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance
 
    def __init__(self):
        if(self.__initialized): return
        else: self.__initialized = True
