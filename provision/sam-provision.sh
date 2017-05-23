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
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME="sam141";fi
CONTAINER_NAME=$IMAGE_NAME".redhat.com"

# Make sam container and get its ip
# Keep existed sam container.

docker ps -a|grep $CONTAINER_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo $CONTAINER_NAME "is exist!needn't to create new one"
fi
echo "begin to test container hostname"
docker run --privileged -itd --hostname $CONTAINER_NAME --name $CONTAINER_NAME -v /dev/log:/dev/log --net=none $IMAGE_NAME bash
issuccess=$?
if [ $issuccess -eq 0 ]
then
   echo $CONTAINER_NAME "success to create!"
else
   echo "Failed to create" $CONTAINER_NAME
fi
pipework br0  $CONTAINER_NAME  dhclient
docker exec -i $CONTAINER_NAME /usr/sbin/sshd -D &
SAM_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`


echo SAM_IP=$SAM_IP>>RESOURCES.txt
echo SAM_HOSTNAME=$CONTAINER_NAME>>RESOURCES.txt
echo REMOTE_IP=$SAM_IP>>RESOURCES.txt
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