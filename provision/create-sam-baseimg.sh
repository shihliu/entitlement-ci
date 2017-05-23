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
    SAMIMG_NAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
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
if [ "$SAMIMG_NAME" == "" ]; then SAMIMG_NAME="sam141"; fi

# Make rhel68 base img
pushd $WORKSPACE/entitlement-ci/provision

docker images|grep $IMAGE_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo $IMAGE_NAME"is exist"
else
   docker build -t $IMAGE_NAME .
   docker tag $IMAGE_NAME $IMAGE_NAME'-slave'
fi

# Make SAM-1.4.1-RHEL-6-20141113.0 base img
docker images|grep $SAMIMG_NAME
isSatExist=$? 
if [ $isSatExist -eq 0 ]
then
  echo $SAMIMG_NAME "is exist, we needn't to delete the old one"
else
  echo $SAMIMG_NAME "is not exist, start to create a new one"
  mv Dockerfile Dockerfile-bk
  mv Dockerfile-sam Dockerfile
  docker build -t $SAMIMG_NAME .
  mv Dockerfile Dockerfile-sam
fi
mv Dockerfile-bk Dockerfile

popd
