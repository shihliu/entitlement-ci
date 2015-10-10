'''
Run command in remote machine with paramiko
'''
import sys, re, time
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
    def remote_run(self, cmd, remote_ip, username, password, timeout, comments, showlogger=True):
        """
        Executes SSH command on remote machine.
        """
        logger.info("Command run in: %s, purpose: %s" % (remote_ip, comments))
        if showlogger:
            logger.info(">>>Remote Run: %s" % cmd)
        retcode, stdout = self.run_paramiko(cmd, remote_ip, username, password, timeout)
        if showlogger:
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
        #trying to resolve large output issue
        ssh._transport.window_size = 2147483647
        if timeout == None:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            retcode = stdout.channel.recv_exit_status()
#             logger.debug("Error : %s" % stderr.read())
#             logger.debug("Return Code : %s" % retcode)
#             logger.debug("Output : \n%s" % stdout.read())
            stderr_output = stderr.read()
            stdout_output = stdout.read()
            ssh.close()
            return retcode, stderr_output if stderr_output != "" else stdout_output
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

    @classmethod
    def run_paramiko_interact(self, cmd, remote_ip, username, password, timeout=None):
        """Execute the given commands in an interactive shell."""
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, 22, username, password)
        channel = ssh.get_transport().open_session()
#         channel.settimeout(600)
        channel.settimeout(6000)
        channel.get_pty()
        channel.exec_command(cmd)
        output = ""
        while True:
#             data = channel.recv(1048576)
            data = channel.recv(1073741824)
            output += data
            logger.debug("output: %s" % data)
            if channel.send_ready():
                if data.strip().endswith('yes/no)?'):
                    logger.debug("interactive input: yes")
                    channel.send("yes" + '\n')
                if data.strip().endswith('\'s password:'):
                    logger.debug("interactive input: red2015")
                    channel.send("red2015" + '\n')
                if data.strip().endswith('[Foreman] Username:'):
                    logger.debug("interactive input: admin")
                    channel.send("admin" + '\n')
                if data.strip().endswith('[Foreman] Password for admin:'):
                    logger.debug("interactive input: admin")
                    channel.send("admin" + '\n')
                if channel.exit_status_ready():
                    break
        if channel.recv_ready():
#             data = channel.recv(1048576)
            data = channel.recv(1073741824)
            output += data
        return channel.recv_exit_status(), output
