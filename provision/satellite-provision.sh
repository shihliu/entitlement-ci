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
if [ "$IMAGE_NAME" == "" ] && [ "$SERVER_COMPOSE" == "ohsnap-satellite" ]; then IMAGE_NAME="satellite62-ohsnap"; \
else IMAGE_NAME="sat-cdn";fi
CONTAINER_NAME=$IMAGE_NAME".redhat.com"

# Make satellite container and get its ip
# Delete existed satellite container to create a new one

docker ps -a|grep $CONTAINER_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo $CONTAINER_NAME "is exist!need to delete to create new one"
   docker stop $CONTAINER_NAME
   docker rm $CONTAINER_NAME
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
SATELLITE_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`


echo SATELLITE_IP=$SATELLITE_IP>>RESOURCES.txt
echo SATELLITE_HOSTNAME=$CONTAINER_NAME>>RESOURCES.txt
echo REMOTE_IP=$SATELLITE_IP>>RESOURCES.txt
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

:<<eof
# Make satellite container and get its ip
# Keep the existed satellite container if it is exist
docker ps -a|grep $CONTAINER_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo $CONTAINER_NAME "is exist!"
else
   echo "begin to test container hostname"
   docker run --privileged -itd --hostname $CONTAINER_NAME --name $CONTAINER_NAME -v /dev/log:/dev/log --net=none $IMAGE_NAME bash
   issuccess=$?
   if [ $issuccess -eq 0 ]
   then
      echo $CONTAINER_NAME "success to create!"
   else
      echo "Failed to create" $CONTAINER_NAME
   fi
   echo TRIGGER_NEXT=True>>$WORKSPACE/TRIGGER_NEXT.txt
fi
pipework br0  $CONTAINER_NAME  dhclient
docker exec -i $CONTAINER_NAME /usr/sbin/sshd -D &
SATELLITE_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`
eof