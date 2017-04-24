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
    --containername=*)
    CONTAINER_NAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
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
if [ "$RHEVMIMG_NAME" == "" ] && [ "$RHEL_COMPOSE" =~ "RHEL-7" ]; then RHEVMIMG_NAME="rhevm4"; \
else RHEVMIMG_NAME="rhevm36";fi
CONTAINER_NAME=$IMAGE_NAME".redhat.com"

docker ps -a|grep $CONTAINER_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo $CONTAINER_NAME "is exist!need to delete to create new one"
   docker stop $CONTAINER_NAME
   docker rm $CONTAINER_NAME
fi
echo "begin to test container hostname"
if [[ $RHEL_COMPOSE =~ "RHEL-7" ]]
then
    docker run --privileged -itd -v /sys/fs/cgroup:/sys/fs/cgroup --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEVMIMG_NAME /usr/sbin/init
else
    docker run --privileged -itd --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEVMIMG_NAME bash
fi
issuccess=$?
if [ $issuccess -eq 0 ]
then
   echo $CONTAINER_NAME "success to create!"
else
   echo "Failed to create" $CONTAINER_NAME
fi
pipework br0  $CONTAINER_NAME  dhclient
docker exec -i $CONTAINER_NAME /usr/sbin/sshd -D &

if [[ $RHEL_COMPOSE =~ "RHEL-7" ]]
then
    docker exec -i $CONTAINER_NAME ifconfig
    RHEVM_IP=`docker exec -i $CONTAINER_NAME ifconfig eth1 | grep "inet "|awk '{print $2}'`
else
    RHEVM_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`
fi

echo RHEVM_IP=$RHEVM_IP>>RESOURCES.txt
echo RHEVM_HOSTNAME=$CONTAINER_NAME>>RESOURCES.txt
echo REMOTE_IP=$RHEVM_IP>>RESOURCES.txt
echo REMOTE_HOSTNAME=$CONTAINER_NAME>>RESOURCES.txt

echo "Provisioning with the following environment"
echo "-------------------------------------------"
echo "SITE:                     $SITE"

if [ "$RESOURCES_DIR" != "" ]; then
   export RESOURCES_OUTPUT=$RESOURCES_DIR/RESOURCES.txt
else
   export RESOURCES_OUTPUT=$WORKSPACE/RESOURCES.txt
fi
cat $RESOURCES_OUTPUT
