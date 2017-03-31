#!/bin/bash

# Parse command line arguments
for i in "$@"
do
case $i in
    --site=*)
    SITE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --ssh_keyfile=*)
    SSH_KEYFILE=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --imagename=*)
    IMAGE_NAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --help)
    HELP=True
    ;;
    *)
    echo "Unknown option $i"        # unknown option
    HELP=True
    ;;
esac
done

if [ "$SITE" == "" ]; then SITE=`hostname`; fi
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME=$RHEL_COMPOSE; fi

# Make rhel base img
RHEL_IMAGE_NAME=$(echo $IMAGE_NAME | tr '[A-Z]' '[a-z]')
echo RHEL_IMAGE_NAME=$RHEL_IMAGE_NAME

# Check RHEL_IMAGE_NAME and remove the old one.
docker images|grep $RHEL_IMAGE_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo "old" $RHEL_IMAGE_NAME "is exist"
   # Stop and rm all RHEL_IMAGE_NAME related containers
   docker ps -a | grep $RHEL_IMAGE_NAME | awk '{print $1}' | xargs docker stop | xargs docker rm
   # Rm RHEL_IMAGE_NAME
   docker rmi -f $RHEL_IMAGE_NAME
fi

# Create the new RHEL_IMAGE_NAME
echo compose_name=$RHEL_COMPOSE
export redhat_root='/redhat_image/rootfs'
echo redhat_root=$redhat_root
if [ ! -d $redhat_root ]; then
   echo $redhat_root "is not exist"
else
   echo $redhat_root "is exist, it should be deleted"
   rm -rf $redhat_root
fi
mkdir -p $redhat_root
wget http://10.66.144.9/home/shihliu/define.repo
mv define.repo /etc/yum.repos.d
echo $compose_name
sed -i -e 's/'rhelbuild'/'$RHEL_COMPOSE'/g' /etc/yum.repos.d/define.repo
rpm --root $redhat_root --initdb
yum -y reinstall --downloadonly --downloaddir . redhat-release
rpm --root $redhat_root -ivh redhat-release*.rpm
rpm --root $redhat_root --import  $redhat_root/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
cp /etc/yum.repos.d/define.repo $redhat_root/etc/yum.repos.d
yum -y --installroot=$redhat_root --setopt=tsflags='nodocs' --setopt=override_install_langs=en_US.UTF-8 install yum
sed -i "/distroverpkg=redhat-release/a override_install_langs=en_US.UTF-8\ntsflags=nodocs" $redhat_root/etc/yum.conf
cp /etc/resolv.conf $redhat_root/etc
chroot $redhat_root /bin/bash yum clean all
tar -C $redhat_root -c . | docker import - $RHEL_IMAGE_NAME
