'''
Run command in remote machine with paramiko
'''
import sys, re
# import pexpect
from utils import logger

try:
    import paramiko
except ImportError:
    print "paramiko not installed, only local run supported"

class RemoteSH(object):
    """
    Run shell in remote machine via paramiko
    """
    @classmethod
    def remote_run(self, cmd, remote_ip, username, password, timeout, comments):
        """
        Executes SSH command on remote machine.
        """
        if comments:
            logger.info(">>>Remote Run: %s" % cmd)
        retcode, stdout = self.run_paramiko(cmd, remote_ip, username, password, timeout)
#         regex = re.compile(r'\x1b\[\d\d?m')
#         if stdout:
#             stdout = stdout.decode('utf-8')
#             stdout = u"".join(stdout).split("\n")
#             output = [
#                 regex.sub('', line) for line in stdout if not line.startswith("[")
#                 ]
#         else:
#             output = []
#         if output:
#             logger.debug("<<<\n%s" % '\n'.join(output[:-1]))
        if comments:
            logger.info("<<<Return Code: %s" % retcode)
            logger.info("<<<Output:\n%s" % stdout)
        return retcode, stdout

    @classmethod
    def remote_get(self, remote_ip, username, password, from_path, to_path):
        logger.info(">>> remote_get")
        scp = paramiko.Transport((remote_ip, 22))
        scp.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(scp)
        # Copy a remote file from the SFTP server to the local host
        sftp.get(from_path, to_path)
        scp.close()
        logger.info("<<< remote_get")

    @classmethod
    def remote_put(self, remote_ip, username, password, from_path, to_path):
        logger.info(">>> remote_put")
        scp = paramiko.Transport((remote_ip, 22))
        scp.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(scp)
        # Copy a local file to the SFTP server
        sftp.put(from_path, to_path)
        scp.close()
        logger.info("<<< remote_put")

    @classmethod
    def run_paramiko(self, cmd, remote_ip, username, password, timeout=None):
        # paramiko.util.log_to_file('/tmp/test')
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, 22, username, password)
        if timeout == None:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            retcode = stdout.channel.recv_exit_status()
#             logger.info("Error : %s" % stderr.read())
#             logger.info("Return Code : %s" % retcode)
#             logger.info("Output : \n%s" % stdout.read())
            ssh.close()
            return retcode, stdout.read() or stderr.read()
        else:
            import time, socket
            from select import select
            channel = ssh.get_transport().open_session()
            channel.settimeout(timeout)
            channel.exec_command(cmd)

            terminate_time = time.time() + timeout
            while True:
                try:
                    rlist, wlist, elist = select([channel], [], [], float(timeout))
                    while (not channel.recv_ready() and
                           not channel.recv_stderr_ready() and
                           terminate_time > time.time()):
                        logger.debug("Command running, wait 1 minute ...")
                        time.sleep(60)
                    if rlist is not None and len(rlist) > 0:
                        if channel.exit_status_ready():
                            stdout = channel.recv(1048576)
                            stderr = channel.recv_stderr(1048576)
                            retcode = channel.recv_exit_status()
                            return retcode, stdout
                    elif elist is not None and len(elist) > 0:
                        if channel.recv_stderr_ready():
                            stdout = channel.recv(1048576)
                            stderr = channel.recv_stderr(1048576)
                            return -1, stdout
                    if terminate_time < time.time():
                        logger.debug("Command timeout exceeded ...")
                        return -1, "Command timeout exceeded ..."
                        
                except socket.timeout:
                    logger.debug("SSH channel timeout exceeded ...")
                    return -1, "SSH channel timeout exceeded ..."

    def run_paramiko_interact(self, cmd, remote_ip, username, password, timeout=None):
        """Execute the given commands in an interactive shell."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, 22, username, password)
        chan = ssh.invoke_shell()
        stdout = ""
        while True:
            stdout += chan.recv(9999)
            if stdout.endswith('yes/no)?'):
                chan.send("yes" + '\n')
            if stdout.endswith('\'s password:'):
                chan.send("red2015")
            if stdout.endswith(']#'):
                retcode = chan.recv_exit_status()
                return retcode, stdout
