from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException
import socket

class HYPERVBase(VIRTWHOBase):
    def hyperv_run_cmd(self, cmd, targetmachine_ip=""):
        hyperv_ip = "10.66.128.9"
#         hyperv_port = get_exported_param("HYPERV_PORT")
#         logger.info("hyperv_port is %s" % hyperv_port)        
        hyperv_port = 6555
#         hyperv_port = int(hyperv_port_old)
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
        s.close()  # close the socket
