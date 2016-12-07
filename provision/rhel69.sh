#!/bin/bash

export compose_name=RHEL-6.9-20161201.0
echo compose_name=$compose_name
export redhat_root='/redhat_image/rootfs'
echo redhat_root=$redhat_root
wget http://10.66.144.9/home/shihliu/define.repo
mv define.repo /etc/yum.repos.d
echo $compose_name
sed -i -e 's/'rhelbuild'/'$compose_name'/g' /etc/yum.repos.d/define.repo
mkdir -p $redhat_root
rpm --root $redhat_root --initdb
yum -y reinstall --downloadonly --downloaddir . redhat-release
rpm --root $redhat_root -ivh redhat-release*.rpm
rpm --root $redhat_root --import  $redhat_root/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
cp /etc/yum.repos.d/define.repo $redhat_root/etc/yum.repos.d
yum -y --installroot=$redhat_root --setopt=tsflags='nodocs' --setopt=override_install_langs=en_US.UTF-8 install yum
sed -i "/distroverpkg=redhat-release/a override_install_langs=en_US.UTF-8\ntsflags=nodocs" $redhat_root/etc/yum.conf
cp /etc/resolv.conf $redhat_root/etc
chroot $redhat_root /bin/bash yum install -y virt-who libvirt
chroot $redhat_root /bin/bash yum install -y openssh-server net-tools

chroot $redhat_root /bin/bash yum clean all
tar -C $redhat_root -c . | docker import - redhat69
