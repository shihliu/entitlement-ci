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
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME=$RHEL_COMPOSE; fi
if [ "$CONTAINER_NAME" == "" ]; then CONTAINER_NAME="rhel.redhat.com";fi

if [ "$RHEL_COMPOSE"x != "release"x ] 
then
  RHEL_IMAGE_NAME=$(echo $IMAGE_NAME | tr '[A-Z]' '[a-z]')
  echo RHEL_IMAGE_NAME=$RHEL_IMAGE_NAME
else
  RHEL_IMAGE_NAME=$IMAGE_NAME

export PASS='red2015'

docker ps -a|grep $CONTAINER_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo $CONTAINER_NAME "is exist!need to delete to create new one"
   docker stop $CONTAINER_NAME
   docker rm $CONTAINER_NAME
fi
echo $CONTAINER_NAME "is not exist"
docker run --privileged -itd --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEL_IMAGE_NAME bash
pipework br0  $CONTAINER_NAME  dhclient
#docker exec -i $CONTAINER_NAME hostname $CONTAINER_NAME
docker exec -i $CONTAINER_NAME hostname
docker exec -i $CONTAINER_NAME yum install -y openssh-server net-tools passwd
docker exec -i $CONTAINER_NAME sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
docker exec -i $CONTAINER_NAME ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
docker exec -i $CONTAINER_NAME ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
docker exec -i $CONTAINER_NAME /usr/sbin/sshd -D &
echo -e "$PASS\n$PASS" | docker exec -i $CONTAINER_NAME /usr/bin/passwd
REMOTE_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`
echo REMOTE_IP=$REMOTE_IP>>RESOURCES.txt
echo REMOTE_HOSTNAME=$CONTAINER_NAME>>RESOURCES.txt

echo "Provisioning with the following environment"
echo "-------------------------------------------"
echo "SITE:                     $SITE"
echo "REMOTE_HOSTNAME:           $CONTAINER_NAME"
echo "REMOTE_IP:             $REMOTE_IP"

if [ "$RESOURCES_DIR" != "" ]; then
   export RESOURCES_OUTPUT=$RESOURCES_DIR/RESOURCES.txt
else
   export RESOURCES_OUTPUT=$WORKSPACE/RESOURCES.txt
fi
cat $RESOURCES_OUTPUT