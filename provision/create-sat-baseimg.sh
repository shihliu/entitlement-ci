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

if [ "$SITE" == "" ]; then SITE="10.66.144.12"; fi
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME="rhel68"; fi
if [ "$SATIMG_NAME" == "" ]; then SATIMG_NAME="satellite62"; fi
# Make rhel68 base img
pushd $WORKSPACE/entitlement-ci/provision

docker images|grep $IMAGE_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo $IMAGE_NAME"is exist"
else
   docker build -t $IMAGE_NAME .
fi
# Make satellite62 base img
docker images|grep $SATIMG_NAME
isSatExist=$? 
if [ $isSatExist -eq 0 ]
then
   #echo $SATIMG_NAME "is exist,need to delete old img"
   echo $SATIMG_NAME "is exist"
   #docker rmi -f $SATIMG_NAME
else
   mv Dockerfile Dockerfile-rhel
   mv Dockerfile-sat Dockerfile
   docker build -t $SATIMG_NAME .
   mv Dockerfile Dockerfile-sat
   #mv Dockerfile-rhel Dockerfile-first
   mv Dockerfile-rhel Dockerfile
fi

# Make rhel68 new img in order to run nosetests
#mv Dockerfile-sec Dockerfile
#docker build -t $IMAGE_NAME .
#mv Dockerfile Dockerfile-sec
#mv Dockerfile-first Dockerfile
popd
