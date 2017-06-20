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
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME="rhel73"; fi
if [ "$SATIMG_NAME" == "" ]
then
  if [ "$SERVER_COMPOSE" == "ohsnap-satellite" ]
  then
    SATIMG_NAME="satellite62-ohsnap"
  elif [ "$SERVER_COMPOSE" == "ohsnap-satellite63" ]
    SATIMG_NAME="satellite63-ohsnap"
  else 
    SATIMG_NAME="sat-cdn"
  fi
fi

# Make rhel73 base img
#pushd $WORKSPACE/entitlement-ci/provision

#docker images|grep $IMAGE_NAME
#isRhelExist=$?
#if [ $isRhelExist -eq 0 ]
#then
#   echo $IMAGE_NAME"is exist"
#else
#   docker build -t $IMAGE_NAME .
#   docker tag $IMAGE_NAME $IMAGE_NAME'-slave'
#fi


# Make satellite63 or satellite63-ohsnap base img
if [ "$RHEL_COMPOSE" == "release" ]
then
# Make satellite63-ohsnap base img
# Delete existed img to create a new one
  docker images|grep $SATIMG_NAME
  isSatExist=$? 
  if [ $isSatExist -eq 0 ]
  then
     echo $SATIMG_NAME "is exist, we need to delete the old one then create new one"
     #Delete all containers related to satellite image
     docker ps -a | grep $SATIMG_NAME | awk '{print $1}' | xargs docker stop | xargs docker rm
     #Delete all <none> images
     docker images | grep '<none>' | awk '{print $2}' | xargs docker rmi
     #Delete satellite images
     docker rmi $SATIMG_NAME
  else
     echo $SATIMG_NAME "is not exist, start to create a new one"
  fi
  mv Dockerfile Dockerfile-bk
  if [ "$SERVER_COMPOSE" == "ohsnap-satellite" ]
  then
    mv Dockerfile-sat-ohsnap Dockerfile
    docker build -t $SATIMG_NAME .
    mv Dockerfile Dockerfile-sat-ohsnap
  else [ "$SERVER_COMPOSE" == "ohsnap-satellite63" ]
    mv Dockerfile-sat63-ohsnap Dockerfile
    docker build -t $SATIMG_NAME .
    mv Dockerfile Dockerfile-sat63-ohsnap
  fi
  mv Dockerfile-bk Dockerfile
else
  # Make satellite62 released base img
  # Keep the existed satellite62 base img if it is exist
  docker images|grep $SATIMG_NAME
  isSatExist=$? 
  if [ $isSatExist -eq 0 ]
  then
     echo $SATIMG_NAME "is exist, we needn't to delete the old one"
  else
    echo $SATIMG_NAME "is not exist, start to create a new one"
    mv Dockerfile Dockerfile-bk
    mv Dockerfile-sat Dockerfile
    docker build -t $SATIMG_NAME .
    mv Dockerfile Dockerfile-sat
    mv Dockerfile-bk Dockerfile
  fi
fi

popd

