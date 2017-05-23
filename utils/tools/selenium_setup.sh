#!/bin/bash

echo "selenium env setup ..."

if [ ! -f /usr/bin/geckodriver ]
then
    #with vnc
    #yum -y groupinstall 'Server with GUI' &> selenium_setup.txt
    #yum install -y firefox tigervnc-server git python-pip &>> selenium_setup.txt
    #gconftool-2 -s /apps/gnome-session/options/show_root_warning --type=boolean false &>> selenium_setup.txt
    #gconftool-2 -s /apps/gnome-screensaver/idle_activation_enabled --type=boolean false &>> selenium_setup.txt
    #gconftool-2 -s /apps/gnome-power-manager/ac_sleep_display --type=int 0 &>> selenium_setup.txt
    #vncserver -SecurityTypes None &>> selenium_setup.txt
    #systemctl stop firewalld.service &>> selenium_setup.txt
    #wget http://git.app.eng.bos.redhat.com/git/entitlement-ci.git/plain/data/geckodriver -P /usr/bin/ &>> selenium_setup.txt
    #wget http://10.66.144.9/projects/sam-virtwho/firefox/firefox-52.0.tar.bz2 -P /root/ &>> selenium_setup.txt
    #tar -xvf /root/firefox-52.0.tar.bz2 -C /root/ &>> selenium_setup.txt
    #mv /usr/bin/firefox /usr/bin/firefox-old &>> selenium_setup.txt
    #ln -s /root/firefox/firefox /usr/bin/firefox &>> selenium_setup.txt
    #pip install -U selenium &>> selenium_setup.txt
    #chmod 777 /usr/bin/geckodriver &>> selenium_setup.txt
    ##maybe need to handle rhel 7 welcome page, and firefox default
    #echo 'export PYTHONPATH=$PYTHONPATH:/usr/bin/geckodriver' >> /etc/profile
    #echo 'export DISPLAY=:1' >> /etc/profile

    #with Xvfb
    yum -y groupinstall 'Server with GUI' &> selenium_setup.txt
    yum install -y Xvfb firefox tigervnc-server git python-pip &>> selenium_setup.txt
    pip install -U selenium pyvirtualdisplay &>> selenium_setup.txt
    wget http://git.app.eng.bos.redhat.com/git/entitlement-ci.git/plain/data/geckodriver -P /usr/bin/ &>> selenium_setup.txt
    wget http://10.66.144.9/projects/sam-virtwho/firefox/firefox-52.0.tar.bz2 -P /root/ &>> selenium_setup.txt
    tar -xvf /root/firefox-52.0.tar.bz2 -C /root/ &>> selenium_setup.txt
    mv /usr/bin/firefox /usr/bin/firefox-old &>> selenium_setup.txt
    ln -s /root/firefox/firefox /usr/bin/firefox &>> selenium_setup.txt
    chmod 777 /usr/bin/geckodriver &>> selenium_setup.txt
    echo 'export PYTHONPATH=$PYTHONPATH:/usr/bin/geckodriver' >> /etc/profile
fi