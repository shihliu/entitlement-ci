#!/bin/bash
#configure slave for gui testing
yum groupinstall -y 'X Window System' 'Desktop' 'Desktop Platform' > ldtp_setup.txt
yum install -y python-twisted tigervnc-server git >> ldtp_setup.txt
git clone git://anongit.freedesktop.org/git/ldtp/ldtp2.git >> ldtp_setup.txt; cd ldtp2/ >> ldtp_setup.txt; python setup.py build >> ldtp_setup.txt; python setup.py install >> ldtp_setup.txt
gconftool-2 --set /desktop/gnome/interface/accessibility --type=boolean true
gconftool-2 -s /apps/gnome-session/options/show_root_warning --type=boolean false
gconftool-2 -s /apps/gnome-screensaver/idle_activation_enabled --type=boolean false
gconftool-2 -s /apps/gnome-power-manager/ac_sleep_display --type=int 0
vncserver -SecurityTypes None