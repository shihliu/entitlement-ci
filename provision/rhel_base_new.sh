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

# Covert the capital letters to lower letters
RHEL_IMAGE_NAME=$(echo $IMAGE_NAME | tr '[A-Z]' '[a-z]')
echo RHEL_IMAGE_NAME=$RHEL_IMAGE_NAME

# Get docker original img
if [[ "$RHEL_COMPOSE" =~ "RHEL-7" ]]
then 
    export ORIGINAL_RHEL = "rhel7.3"
    echo "ORIGINAL_RHEL is " $ORIGINAL_RHEL
else
    export ORIGINAL_RHEL = "rhel6.8"
    echo "ORIGINAL_RHEL is " $ORIGINAL_RHEL
fi

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
echo original_rhel=$ORIGINAL_RHEL
pushd $WORKSPACE/entitlement-ci/provision

mv Dockerfile Dockerfile-bk
mv Dockerfile-rhel Dockerfile
docker build -t $RHEL_IMAGE_NAME .
mv Dockerfile Dockerfile-rhel
mv Dockerfile-bk Dockerfile

popd

