from utils import *
from testcases.virt_who_polarion.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException
import socket
import re

class HYPERVBase(VIRTWHOBase):
    def hyperv_run_cmd(self, cmd, targetmachine_ip=""):
    # Run cmd on hyperv
        hyperv_ip = self.get_vw_cons("HYPERV_HOST")
        hyperv_port = self.get_vw_cons("HYPERV_PORT")
        # listen to socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to the socket
        s.connect((hyperv_ip, hyperv_port))
        # send the command
        s.sendall(cmd)
        data = ""
        while True:
            buf = s.recv(1024)
            if not len(buf):
                break
            data = data + buf
        logger.info ("After run %s, the output is \n%s" % (cmd, data))
        return data
        # close the socket
        s.close()

    def hyperv_get_guest_ip(self, guest_name, targetmachine_ip=""):
    # Get guest's IP
        output = self.hyperv_run_cmd("(Get-VMNetworkAdapter -VMName %s).IpAddresses" % guest_name)
        if output is not "":
            datalines = output.splitlines()
            for line in datalines:
                if ":" not in line:
                    guest_ip = line
                    logger.info("hyperv guest ip address is %s" % guest_ip)
                    return guest_ip

    def hyperv_get_guest_status(self, guest_name, targetmachine_ip=""):
    # Get guest's status
        output = self.hyperv_run_cmd("Get-VM %s | select *" % guest_name)
        if output is not "":
            logger.info("Success to run command to get vm %s status" % guest_name)
            status = self.get_key_rhevm(output, "State", "VMName", guest_name)
            return status
        else:
            raise FailException("Failed to run command to get vm %s status" % guest_name)

    def hyperv_get_guest_id(self, guest_name, targetmachine_ip=""):
    # Get guest's status
        output = self.hyperv_run_cmd("Get-VM %s | select *" % guest_name)
        if output is not "":
            logger.info("Success to run command to get vm %s ID" % guest_name)
            guest_id = self.get_key_rhevm(output, "Id", "VMName", guest_name)
            logger.info("before decode guest uuid is %s" %guest_id)
            guest_uuid_after_decode = self.decodeWinUUID(guest_id)
            logger.info("after decode guest uuid is %s" %guest_uuid_after_decode)
            return guest_id 
        else:
            raise FailException("Failed to run command to get vm %s ID" % guest_name)

    @classmethod
    def decodeWinUUID(cls, uuid):
    # Decode host and guest uuid in hyperv
        """ Windows UUID needs to be decoded using following key
        From: {78563412-AB90-EFCD-1234-567890ABCDEF}
        To:    12345678-90AB-CDEF-1234-567890ABCDEF
        """
        if uuid[0] == "{":
            s = uuid[1:-1]
        else:
            s = uuid
        return s[6:8] + s[4:6] + s[2:4] + s[0:2] + "-" + s[11:13] + s[9:11] + "-" + s[16:18] + s[14:16] + s[18:]

    def hyperv_get_guest_guid(self, guest_name, targetmachine_ip=""):
    # Get guest's guid
        output = self.hyperv_run_cmd('gwmi -namespace "root\\virtualization\\v2" Msvm_VirtualSystemSettingData | select ElementName, BIOSGUID')
        if output is not "":
            datalines = output.splitlines()
            segs = []
            for line in datalines:
                segs.append(line)
            for item in segs:
                if guest_name in item:
                    item = item.strip()
                    before_guest_uuid = item[item.index("{")+1:item.index("}")].strip()
                    logger.info("Before decode, guest %s guid is %s" %(guest_name,before_guest_uuid))
                    guest_uuid = self.decodeWinUUID("%s" %before_guest_uuid)
                    logger.info("After decode, guest %s guid is %s" %(guest_name,before_guest_uuid))
                    return guest_uuid
        else:
            raise FailException("Failed to run command to get vm %s ID" %guest_name)

    def hyperv_get_host_uuid(self, targetmachine_ip=""):
    # Get host's uuid
        output = self.hyperv_run_cmd('gwmi -namespace "root/cimv2" Win32_ComputerSystemProduct | select UUID ')
        datalines = output.splitlines()
        for line in datalines:
            if "--" not in line and "UUID" not in line:
                host_uuid = self.decodeWinUUID("%s" %line)
                logger.info("Success to get hyperv's uuid after decode, uuid is %s" %host_uuid)
                return host_uuid

    def hyperv_start_guest(self, guest_name, targetmachine_ip=""):
     # Start hyperv guest
        output = self.hyperv_run_cmd("Start-VM -Name %s" % guest_name)
        if output is "":
            logger.info("Success to run command to start vm %s" % guest_name)
            time.sleep(10)
            status = self.hyperv_get_guest_status(guest_name)
            if "Running" in status:
                logger.info("Success to show vm %s status is running" % guest_name)
                runtime = 0
                while True:
                    time.sleep(10)
                    guest_ip = self.hyperv_get_guest_ip(guest_name)
                    if guest_ip is None:
                        runtime = runtime + 1
                        time.sleep(20)
                        if runtime > 10:
                            raise FailException("Failed to start vm %s" % guest_name)
                    else:
                        logger.info("Success to start vm %s and ip is %s" % (guest_name, guest_ip))
                        break
            else:
                logger.info("Failed to show vm %s status is running" % guest_name)
        else:
            raise FailException("Failed to run command to start vm %s" % guest_name)

    def hyperv_stop_guest(self, guest_name, targetmachine_ip=""):
    # Stop hyperv guest
        output = self.hyperv_run_cmd("Stop-VM -Name %s" % guest_name)
        if output is "":
            logger.info("Success to run stop command vm %s" % guest_name)
            status = self.hyperv_get_guest_status(guest_name)
            if "Off" in status:
                logger.info("Success to stop vm %s" % guest_name)
            else:
                raise FailException("Failed to stop vm %s" % guest_name)
        else:
            raise FailException("Failed to stop command vm %s" % guest_name)

    def hyperv_suspend_guest(self, guest_name, targetmachine_ip=""):
    # Suspend hyperv guest
        output = self.hyperv_run_cmd("Suspend-VM -Name %s" % guest_name)
        if output is "":
            logger.info("Success to run suspend command vm %s" % guest_name)
            status = self.hyperv_get_guest_status(guest_name)
            if "Paused" in status:
                logger.info("Success to suspend vm %s" % guest_name)
            else:
                raise FailException("Failed to suspend vm %s" % guest_name)
        else:
            raise FailException("Failed to suspend command vm %s" % guest_name)

    def hyperv_resume_guest(self, guest_name, targetmachine_ip=""):
    # Resume hyperv guest
        output = self.hyperv_run_cmd("Resume-VM -Name %s" % guest_name)
        if output is "":
            logger.info("Success to run Resume command vm %s" % guest_name)
            status = self.hyperv_get_guest_status(guest_name)
            if "Running" in status:
                logger.info("Success to suspend vm %s" % guest_name)
            else:
                raise FailException("Failed to suspend vm %s" % guest_name)
        else:
            raise FailException("Failed to suspend command vm %s" % guest_name)

    def update_vm_hyperv_configure(self, hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password, debug=1, targetmachine_ip=""):
    # Configure hyperv mode in /etc/sysconfig/virt-who
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/.*VIRTWHO_HYPERV=.*/VIRTWHO_HYPERV=1/g' -e 's/.*VIRTWHO_HYPERV_OWNER=.*/VIRTWHO_HYPERV_OWNER=%s/g' -e 's/.*VIRTWHO_HYPERV_ENV=.*/VIRTWHO_HYPERV_ENV=%s/g' -e 's/.*VIRTWHO_HYPERV_SERVER=.*/VIRTWHO_HYPERV_SERVER=%s/g' -e 's/.*VIRTWHO_HYPERV_USERNAME=.*/VIRTWHO_HYPERV_USERNAME=%s/g' -e 's/.*VIRTWHO_HYPERV_PASSWORD=.*/VIRTWHO_HYPERV_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (debug, hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password)
        ret, output = self.runcmd(cmd, "Setting hyperv mode in /etc/sysconfig/virt-who.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set hyperv mode in /etc/sysconfig/virt-who.")
        else:
            raise FailException("Test Failed - Failed  to set hyperv mode in /etc/sysconfig/virt-who.")

    # ========================================================
    #       Hyperv - test env set up function
    # ========================================================
    def hyperv_setup(self):
    # Set hyperv test env. including:
    # 1. Configure virt-who run at hyperv mode
    # 2. Register system to server 
        server_ip, server_hostname, server_user, server_pass = self.get_server_info()
        hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
        hyperv_host = self.get_vw_cons("HYPERV_HOST")
        self.update_vm_hyperv_configure(hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password)
        self.vw_restart_virtwho()
        self.sub_unregister()
        self.configure_server(server_ip, server_hostname)
        self.sub_register(server_user, server_pass)
        guest_name = self.get_vw_guest_name("HYPERV_GUEST_NAME")
#         self.wget_images(self.get_vw_cons("esx_guest_url"), guest_name, hyperv_host)
#         self.esx_add_guest(guest_name, hyperv_host)
#         self.hyperv_start_guest(guest_name, hyperv_host)
#         # self.esx_service_restart(ESX_HOST)
#         self.hyperv_stop_guest(guest_name, hyperv_host)
        self.vw_restart_virtwho()

