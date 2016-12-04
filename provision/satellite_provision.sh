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

if [ "$SITE" == "" ]; then SITE="10.16.46.37"; fi
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME="satellite62"; fi
if [ "$CONTAINER_NAME" == "" ]; then CONTAINER_NAME="satellite62.redhat.com";fi
# Set some defaults if values not assigned
# if [ "$DOCKERFILE" == "" ]; then DOCKERFILE="/root/.";
# else
  #Build satellite62 IMAGE
#Provision satellite
docker run --privileged -itd  --name $CONTAINER_NAME --net=none $IMAGE_NAME bash
pipework br0  $CONTAINER_NAME  dhclient
docker exec -i $CONTAINER_NAME hostname $CONTAINER_NAME
docker exec -i $CONTAINER_NAME /usr/sbin/sshd -D &
# docker exec -i $CONTAINER_NAME export PATH=$PATH:/sbin/|service sshd restart
# docker exec -i $CONTAINER_NAME export PATH=$PATH:/sbin/|service sshd status
# docker exec -i $CONTAINER_NAME yum install -y satellite
SATELLITE_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`
#SATELLITE_IP=docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:" | awk '{print $2}' | cut -c 6-
echo SATELLITE_IP=$SATELLITE_IP>>RESOURCES.txt
echo SATELLITE_HOSTNAME=$CONTAINER_NAME>>RESOURCES.txt
echo REMOTE_IP=$SATELLITE_IP>>RESOURCES.txt
echo REMOTE_HOSTNAME=$CONTAINER_NAME>>RESOURCES.txt
export REMOTE_IP=$SATELLITE_IP
export REMOTE_HOSTNAME=$CONTAINER_NAME
# fi
#
echo "Provisioning with the following environment"
echo "-------------------------------------------"
echo "SITE:                     $SITE"
echo "SATELLITE_NAME:           $CONTAINER_NAME"
echo "SATELLITE_IP:             $SATELLITE_IP"

if [ "$RESOURCES_DIR" != "" ]; then
   export RESOURCES_OUTPUT=$RESOURCES_DIR/RESOURCES.txt
else
   export RESOURCES_OUTPUT=$WORKSPACE/RESOURCES.txt
fi
cat $RESOURCES_OUTPUT
popd