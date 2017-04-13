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
    --satimgname=*)
    SATIMG_NAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
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
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME="rhel68"; fi
if [ "$SATIMG_NAME" == "" ] && [ "$SERVER_COMPOSE" == "ohsnap-satellite" ]; then SATIMG_NAME="satellite62-ohsnap"; \
else SATIMG_NAME="sat62";fi

# Make rhelx.x base img
pushd $WORKSPACE/entitlement-ci/provision

#Get "rhel6.x"
#RHEL_COMPOSE_SIMPLE=${RHEL_COMPOSE:0:8}
#RHEL_COMPOSE_RESULT=${RHEL_COMPOSE_SIMPLE//-/}
#IMAGE_NAME=$( tr '[A-Z]' '[a-z]' <<< $RHEL_COMPOSE_RESULT)

docker images|grep $IMAGE_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo $IMAGE_NAME"is exist, it neend't to pull it from repo"
else
   docker pull registry.access.redhat.com/$IMAGE_NAME
   docker tag registry.access.redhat.com/$IMAGE_NAME $IMAGE_NAME
   docker rmi registry.access.redhat.com/$IMAGE_NAME
   docker run --privileged -itd --name $IMAGE_NAME $IMAGE_NAME bash
   docker exec -i $IMAGE_NAME subscription-manager register --username=qa@redhat.com --password=uuV4gQrtG7sfMP3q --auto-attach
   docker exec -i $IMAGE_NAME yum install -y openssh-server net-tools passwd
   docker commit $IMAGE_NAME $IMAGE_NAME
   docker stop $IMAGE_NAME
   docker rm $IMAGE_NAME
   #docker run -it $IMAGE_NAME subscription-manager register --username=qa@redhat.com --password=uuV4gQrtG7sfMP3q --auto-attach
   #CONATIMER_ID=`docker ps -a |grep $IMAGE_NAME|awk '{print $1}'`
   #echo "after register ,container id is " $CONATIMER_ID
   #docker commit $CONATIMER_ID $IMAGE_NAME
   #docker rm $CONATIMER_ID
   #docker run -it $IMAGE_NAME yum install -y openssh-server net-tools passwd
   #CONATIMER_ID=`docker ps -a |grep $IMAGE_NAME|awk '{print $1}'`
   #echo "after register ,container id is " $CONATIMER_ID
   #docker commit $CONATIMER_ID $IMAGE_NAME
   #docker rm $CONATIMER_ID
fi