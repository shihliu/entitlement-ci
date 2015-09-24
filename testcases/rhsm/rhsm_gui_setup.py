from utils import *
from utils.tools.shell import command
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException
from testcases.rhsm.rhsmconstants import RHSMConstants

class rhsm_gui_setup(RHSMGuiBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.rhsm_gui_sys_setup()
            self.configure_server()
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def rhsm_gui_sys_setup(self):
        # in rhel 6, run yum groupinstall -y 'X Window System' 'Desktop' 'Desktop Platform' instead
        # yum install -y python-twisted tigervnc-server git
        if command.get_os_serials() == "7":
            cmd = "yum install -y @gnome-desktop tigervnc-server pexpect pyatspi"
            ret, output = command.runcmd(cmd, "install gui related packages", showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install @gnome-desktop tigervnc-server pexpect pyatspi")
            else:
                raise FailException("Test Failed - Failed to install @gnome-desktop tigervnc-server pexpect pyatspi")
        else:
            cmd = "yum groupinstall -y 'X Window System' 'Desktop' 'Desktop Platform'"
            ret, output = command.runcmd(cmd, "install desktop", showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install 'X Window System' 'Desktop' 'Desktop Platform'")
            else:
                raise FailException("Test Failed - Failed to install 'X Window System' 'Desktop' 'Desktop Platform'")
            cmd = "yum install -y python-twisted tigervnc-server git"
            ret, output = command.runcmd(cmd, "install gui related packages", showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install python-twisted tigervnc-server git")
            else:
                raise FailException("Test Failed - Failed to install python-twisted tigervnc-server git")
            cmd = "gconftool-2 --set /desktop/gnome/interface/accessibility --type=boolean true; gconftool-2 -s /apps/gnome-session/options/show_root_warning --type=boolean false; gconftool-2 -s /apps/gnome-screensaver/idle_activation_enabled --type=boolean false; gconftool-2 -s /apps/gnome-power-manager/ac_sleep_display --type=int 0"
            ret, output = command.runcmd(cmd, "setup desktop for gui testing", showlogger=False)
            if ret == 0:
                logger.info("Succeeded to setup system for gui testing")
            else:
                raise FailException("Test Failed - Failed to setup system for gui testing")
        install_ldtp_cmd = "git clone git://anongit.freedesktop.org/git/ldtp/ldtp2.git; cd ldtp2/; python setup.py build; python setup.py install"
        ret, output = command.runcmd(install_ldtp_cmd, "install ldtp", showlogger=False)
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
        ret, output = command.runcmd(cmd, "set gnome-terminal desktop", showlogger=False)
        if ret == 0:
            logger.info("Succeeded to start ldtp server")
        else:
            raise FailException("Test Failed - Failed to start ldtp server")
        if command.get_os_serials() == "7":
            cmd = "service firewalld stop"
        else:
            cmd = "service iptables stop"
        ret, output = command.runcmd(cmd, "stop iptales")
        if ret == 0:
            logger.info("Succeeded to stop firewalld/iptables")
        else:
            raise FailException("Test Failed - Failed to stop firewalld/iptables")
        cmd = "ps -ef | grep Xvnc | grep -v grep"
        ret, output = command.runcmd(cmd, "check whether vncserver started")
        if ret == 0:
            logger.info("vncserver already started ...")
        else:
            cmd = "vncserver -SecurityTypes None"
            ret, output = command.runcmd(cmd, "start vncserver")
            if ret == 0:
                logger.info("Succeeded to start vncserver")
            else:
                raise FailException("Test Failed - Failed to start vncserver")

if __name__ == "__main__":
    unittest.main()
