from utils import *
from utils.tools.shell.remotesh import RemoteSH
from utils.tools.shell.localsh import LocalSH
from utils.exception.failexception import FailException

class Command(object):
    remote_ip = username = password = ""
    def __init__(self, remote_ip=None, username=None, password=None):
        if remote_ip != "" and remote_ip != None:
            self.remote_ip = remote_ip
            self.username = username
            self.password = password
            # logger.info("command run in: %s" % self.remote_ip)
        else:
            self.remote_ip = get_exported_param("REMOTE_IP")
            self.username = "root"
            self.password = "red2015"
            # logger.info("command run in: %s" % self.remote_ip)

    def run(self, cmd, timeout=None, comments=None, showlogger=True):
        if self.remote_ip == None:
            ret, output = LocalSH.local_run(cmd, timeout, comments, showlogger)
        else:
            ret, output = RemoteSH.remote_run(cmd, self.remote_ip, self.username, self.password, timeout, comments, showlogger)
        return ret, output

    def run_interact(self, cmd, timeout=None, comments=True):
        ret, output = RemoteSH.run_paramiko_interact(cmd, self.remote_ip, self.username, self.password, timeout)
        return ret, output

if __name__ == "__main__":
    commander = Command("10.34.35.76", "root", "red2015")
#     cmd = "virsh migrate --live 5.10_Server_x86_64 qemu+ssh://10.16.67.184/system --undefinesource"
    cmd = "scp /root/images_nfs/test.xml root@10.16.67.184:/root/"
    print commander.run_interact(cmd)
