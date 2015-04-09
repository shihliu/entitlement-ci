from utils.tools.shell.remotesh import RemoteSH
from utils.tools.shell.localsh import LocalSH

class Command(object):
    remote_ip = username = password = None
    def __init__(self, remote_ip=None, username=None, password=None):
        if remote_ip != "" and remote_ip != None:
            self.remote_ip = remote_ip
            self.username = username
            self.password = password

    def run(self, cmd, timeout=None, comments=True):
        if self.remote_ip == None:
            # (ret, output) = commands.getstatusoutput(cmd, timeout)
            ret, output = LocalSH.local_run(cmd, timeout, comments)
        else:
            ret, output = RemoteSH.remote_run(cmd, self.remote_ip, self.username, self.password, timeout)
#             ret, output = RemoteSH.run_pexpect(cmd, self.remote_ip, self.username, self.password, timeout)
        return ret, output

    def remote_put(self, from_path, to_path):
        RemoteSH.remote_put(self.remote_ip, self.username, self.password, from_path, to_path)

    def fork_run(self, cmd):
        import os, sys
        r, w = os.pipe()
        pid = os.fork()
        if pid == 0:
            # subprocess
            os.close(r)
            w = os.fdopen(w, 'w')
            print "child: writing"
            w.write("subprocess running")
            w.close()
        else:
            # parent process
            os.close(w)
            r = os.fdopen(r)
            print "parent: reading"
            txt = r.read()
            print txt

    def interact_run(self, cmd):
        ret, output = LocalSH.run_pexpect(cmd)
        return ret, output

    def git_run(self, git_cmd, git_dir=""):
        # can also pip install gitpython and use it
        ret, output = LocalSH.run_git(git_cmd, git_dir)
        return ret, output

    def get_rhel_version(self, file_name):
        if "RHEL5" in file_name:
            return 5
        elif "RHEL6" in file_name or "RHEL-6" in file_name:
            return 6
        elif "RHEL7" in file_name or "RHEL-7" in file_name:
            return 7
