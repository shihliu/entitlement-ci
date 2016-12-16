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
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME="redhat69"; fi
if [ "$CONTAINER_NAME" == "" ]; then CONTAINER_NAME="rhel69.redhat.com";fi
# Set some defaults if values not assigned
# if [ "$DOCKERFILE" == "" ]; then DOCKERFILE="/root/.";
# else
  #Build satellite62 IMAGE
#Provision satellite
#docker build -t $IMAGE_NAME /root/.
docker run --privileged -itd  --name $CONTAINER_NAME --net=none $IMAGE_NAME bash
pipework br0  $CONTAINER_NAME  dhclient
docker exec -i $CONTAINER_NAME hostname $CONTAINER_NAME
docker exec -i $CONTAINER_NAME yum install -y openssh-server net-tools
docker exec -i $CONTAINER_NAME sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
docker exec -i $CONTAINER_NAME echo "root:red2015" | chpasswd
docker exec -i $CONTAINER_NAME ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
docker exec -i $CONTAINER_NAME ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
docker exec -i $CONTAINER_NAME /usr/sbin/sshd -D &
REMOTE_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`
echo REMOTE_IP=$REMOTE_IP>>RESOURCES.txt
echo REMOTE_HOSTNAME=$CONTAINER_NAME>>RESOURCES.txt
echo export REMOTE_IP=$REMOTE_IP
echo export REMOTE_HOSTNAME=$CONTAINER_NAME

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
popd
