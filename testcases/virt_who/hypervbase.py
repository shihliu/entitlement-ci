from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException
import socket
import re


class HYPERVBase(VIRTWHOBase):
    def hyperv_run_cmd(self, cmd, targetmachine_ip=""):
    # Run cmd on hyperv
        hyperv_ip = self.get_vw_cons("HYPERV_HOST")
        hyperv_port = self.get_vw_cons("HYPERV_PORT")
#         hyperv_port = 6555
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # listen to socket
        s.connect((hyperv_ip, hyperv_port))  # connect to the socket
        s.sendall(cmd)  # send the command
        data = ""
        while True:
            buf = s.recv(1024)
            if not len(buf):
                break
            data = data + buf
        logger.info ("After run %s, the output is \n%s" % (cmd, data))
        return data
        s.close()  # close the socket

    def hyperv_get_guest_ip(self, guest_name, targetmachine_ip=""):
    # Get guest's IP
        output = self.hyperv_run_cmd("(Get-VMNetworkAdapter -VMName %s).IpAddresses" % guest_name)
        if output is not "":
            guest_ip = re.findall(r'\d+.\d+.\d+.\d+', output)
            logger.info("hyperv guest ip address is %s" % guest_ip)
            return guest_ip
#         else:
#             raise FailException("Failed to get hyperv guest ip address")

    def hyperv_get_guest_status(self, guest_name, targetmachine_ip=""):
    # Get guest's status's from guest's detail info
        output = self.hyperv_run_cmd("Get-VM %s | select *" % guest_name)
        if output is not "":
            logger.info("Success to run command to get vm %s status" % guest_name)
            status = self.get_key_rhevm(output, "State", "VMName", guest_name)
            return status
        else:
            raise FailException("Failed to run command to get vm %s status" % guest_name)

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
