from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException
import socket
import re

class HYPERVBase(VIRTWHOBase):
    def hyperv_run_cmd(self, cmd, targetmachine_ip=""):
        hyperv_ip = "10.66.128.9"
        hyperv_port = 6555
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
        output = self.hyperv_run_cmd("(Get-VMNetworkAdapter -VMName %s).IpAddresses" % guest_name)
        if output is not "":
            guest_ip = re.findall(r'\d+.\d+.\d+.\d+', output)
            logger.info("hyperv guest ip address is %s" % guest_ip)
            return guest_ip
#         else:
#             raise FailException("Failed to get hyperv guest ip address")

    def hyperv_get_guest_status(self, guest_name, targetmachine_ip=""):
        output = self.hyperv_run_cmd("Get-VM %s | select *" % guest_name)
        if output is not "":
            logger.info("Success to run command to get vm %s status" % guest_name)
            status = self.get_key_rhevm(output, "State", "VMName", guest_name)
            return status
        else:
            raise FailException("Failed to run command to get vm %s status" % guest_name)

    def hyperv_start_guest(self, guest_name, targetmachine_ip=""):
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
