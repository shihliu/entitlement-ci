from utils import *
from utils.tools.shell.command import Command
from utils.exception.failexception import FailException
from testcases.rhsm.rhsmconstants import RHSMConstants

class rhsm_gui_setup(unittest.TestCase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.rhsm_gui_sys_setup()
            RHSMConstants().configure_testing_server()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def rhsm_gui_sys_setup(self):
        # in rhel 6, run yum groupinstall -y 'X Window System' 'Desktop' 'Desktop Platform' instead
        # yum install -y python-twisted tigervnc-server git
        if RHSMConstants().get_os_serials() == "7":
            cmd = "yum install -y @gnome-desktop tigervnc-server pexpect pyatspi"
            ret, output = RHSMConstants().runcmd(cmd)
            if ret == 0:
                logger.info("Succeeded to install @gnome-desktop tigervnc-server pexpect pyatspi")
            else:
                raise FailException("Test Failed - Failed to install @gnome-desktop tigervnc-server pexpect pyatspi")
        else:
            cmd = "yum groupinstall -y 'X Window System' 'Desktop' 'Desktop Platform'"
            ret, output = RHSMConstants().runcmd(cmd)
            if ret == 0:
                logger.info("Succeeded to install 'X Window System' 'Desktop' 'Desktop Platform'")
            else:
                raise FailException("Test Failed - Failed to install 'X Window System' 'Desktop' 'Desktop Platform'")
            cmd = "yum install -y python-twisted tigervnc-server git"
            ret, output = RHSMConstants().runcmd(cmd)
            if ret == 0:
                logger.info("Succeeded to install python-twisted tigervnc-server git")
            else:
                raise FailException("Test Failed - Failed to install python-twisted tigervnc-server git")
        install_ldtp_cmd = "git clone git://anongit.freedesktop.org/git/ldtp/ldtp2.git; cd ldtp2/; python setup.py build; python setup.py install"
        ret, output = RHSMConstants().runcmd(install_ldtp_cmd)
        if ret == 0:
            logger.info("Succeeded to install ldtp.")
        else:
            raise FailException("Test Failed - Failed to install ldtp.")
        cmd = '''mkdir -p /root/.config/autostart; cat > /root/.config/autostart/gnome-terminal.desktop <<EOF
[Desktop Entry]
Type=Application
Exec=gnome-terminal -e ldtp
Hidden=false
X-GNOME-Autostart-enabled=true
Name=ldtpd
Comment=
EOF
'''
        ret, output = RHSMConstants().runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to start ldtp server")
        else:
            raise FailException("Test Failed - Failed to start ldtp server")
        if RHSMConstants().get_os_serials() == "7":
            cmd = "service firewalld stop"
        else:
            cmd = "service iptables stop"
        ret, output = RHSMConstants().runcmd(cmd)
        if ret == 0:
            logger.info("Succeeded to stop firewalld/iptables")
        else:
            raise FailException("Test Failed - Failed to stop firewalld/iptables")
        cmd = "ps -ef | grep Xvnc | grep -v grep"
        ret, output = RHSMConstants().runcmd(cmd)
        if ret == 0:
            logger.info("vncserver already started ...")
        else:
            cmd = "vncserver -SecurityTypes None"
            ret, output = RHSMConstants().runcmd(cmd)
            if ret == 0:
                logger.info("Succeeded to start vncserver")
            else:
                raise FailException("Test Failed - Failed to start vncserver")

if __name__ == "__main__":
    unittest.main()
