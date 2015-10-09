from utils import *
from utils.tools.shell.remotesh import RemoteSH
from utils.tools.shell.localsh import LocalSH
from utils.exception.failexception import FailException

class Command(object):
    remote_ip = username = password = ""
    def __init__(self, remote_ip=None, username=None, password=None):
        if remote_ip != "" and remote_ip != None:
            # if remote ip provided, run on it
            self.remote_ip = remote_ip
            self.username = username
            self.password = password
        elif get_exported_param("REMOTE_IP") != "":
            # by default, run on env remote ip
            self.remote_ip = get_exported_param("REMOTE_IP")
            self.username = "root"
            self.password = "red2015"
        else:
            raise FailException("REMOTE_IP not provided, failed to run ...")

    def run(self, cmd, timeout=None, comments=None, showlogger=True):
        if self.remote_ip == None:
            ret, output = LocalSH.local_run(cmd, timeout, comments, showlogger)
        else:
            ret, output = RemoteSH.remote_run(cmd, self.remote_ip, self.username, self.password, timeout, comments, showlogger)
        return ret, output

    def run_interact(self, cmd, timeout=None, comments=True):
        ret, output = RemoteSH.run_paramiko_interact(cmd, self.remote_ip, self.username, self.password, timeout)
        return ret, output

def runcmd(cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
    if targetmachine_ip != None and targetmachine_ip != "":
        if targetmachine_user != None and targetmachine_user != "":
            commander = Command(targetmachine_ip, targetmachine_user, targetmachine_pass)
        else:
            commander = Command(targetmachine_ip, "root", "red2015")
    else:
        commander = Command(get_exported_param("REMOTE_IP"), "root", "red2015")
    return commander.run(cmd, timeout, cmddesc, showlogger)

def runcmd_interact(cmd, cmddesc=None, targetmachine_ip=None, targetmachine_user=None, targetmachine_pass=None, timeout=None, showlogger=True):
    if targetmachine_ip != None and targetmachine_ip != "":
        if targetmachine_user != None and targetmachine_user != "":
            commander = Command(targetmachine_ip, targetmachine_user, targetmachine_pass)
        else:
            commander = Command(targetmachine_ip, "root", "red2015")
    else:
        commander = Command(get_exported_param("REMOTE_IP"), "root", "red2015")
    return commander.run_interact(cmd, timeout, cmddesc)

if __name__ == "__main__":
    commander = Command("10.34.35.76", "root", "red2015")
    cmd = "scp /root/images_nfs/test.xml root@10.16.67.184:/root/"
    print commander.run_interact(cmd)
