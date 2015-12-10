from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException
import socket

class HYPERVBase(VIRTWHOBase):
    def hyperv_run_cmd(self, cmd, targetmachine_ip=""):
        hyperv_ip = "10.66.128.9"
        hyperv_port = 6555
#         hyperv_port = int(hyperv_port_old)
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)      # listen to socket
        s.connect((hyperv_ip,hyperv_port))       # connect to the socket
        s.sendall(cmd)      # send the command
        data=s.recv(4096)     # get all the output
        logger.info ("After run %s, the output is \n%s" %(cmd, data))
        s.close()   # close the socket
