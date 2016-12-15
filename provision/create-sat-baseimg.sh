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

if [ "$SITE" == "" ]; then SITE="10.16.46.37"; fi
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME="rhel68"; fi
if [ "$SATIMG_NAME" == "" ]; then SATIMG_NAME="satellite62"; fi
# Make rhel68 base img
pushd $WORKSPACE/entitlement-ci/testcases/provision

docker images|grep $IMAGE_NAME
isRhelExist=$?
if [ $isRhelExist==0 ]
then
   echo $IMAGE_NAME"is exist"
else
   docker build -t $IMAGE_NAME .
fi
# Make satellite62 base img
docker images|grep $SATIMG_NAME
isSatExist=$? 
if [ $isSatExist==0 ]
then
   echo $SATIMG_NAME"is exist"
else
   mv Dockerfile Dockerfile-rhel
   mv Dockerfile-sat Dockerfile
   docker build -t $IMAGE_NAME .
   mv Dockerfile Dockerfile-sat
   mv Dockerfile-rhel Dockerfile 
fi
popd
