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

# docker run --privileged -itd  --name $CONTAINER_NAME --net=none $IMAGE_NAME bash
# pipework br0  $CONTAINER_NAME  dhclient
# docker exec -i $CONTAINER_NAME hostname $CONTAINER_NAME
# docker exec -i $CONTAINER_NAME yum install -y satellite
#SATELLITE_IP=`ssh root@$SITE docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"`| awk '{print $2}' | cut -c 6-`
SATELLITE_IP=docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:" | awk '{print $2}' | cut -c 6-
echo SATELLITE_IP=$SATELLITE_IP>>RESOURCE.txt
# fi
#
echo "Provisioning with the following environment"
echo "-------------------------------------------"
echo "SITE:                     $SITE"
echo "CONTAINER_NAME:           $CONTAINER_NAME"
echo "SATELLITE_IP:             $SATELLITE_IP"
