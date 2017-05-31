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
    --rhevmimgname=*)
    RHEVMIMG_NAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
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
if [ "$RHEVMIMG_NAME" == "" ] 
then
    if [[ "$RHEL_COMPOSE" == "release" ]]
    then
	    #if [[ "$VIRTWHO_SRC" =~ "rhel7" ]]
	    #then
	    #    RHEVMIMG_NAME="rhevm4"
	    #else
	    #    RHEVMIMG_NAME="rhevm36"
	    #fi
	    RHEVMIMG_NAME="rhevm4"
    elif [[ "$RHEL_COMPOSE" =~ "RHEL-7" ]]
    then 
        RHEVMIMG_NAME="rhevm4"
    else 
        RHEVMIMG_NAME="rhevm36"
    fi
else
    RHEVMIMG_NAME="rhevm4"
fi
# Make rhevm base img
pushd $WORKSPACE/entitlement-ci/provision
docker images|grep $RHEVMIMG_NAME
isSatExist=$? 
if [ $isSatExist -eq 0 ]
then
   echo $RHEVMIMG_NAME "is exist, we needn't to delete the old one then create new one"
   #Delete all containers related to rhevm image
   #docker ps -a | grep $RHEVMIMG_NAME | awk '{print $1}' | xargs docker stop | xargs docker rm
   #Delete all <none> images
   #docker images | grep '<none>' | awk '{print $2}' | xargs docker rmi
   #Delete satellite images
   #docker rmi $RHEVMIMG_NAME
else
   echo $RHEVMIMG_NAME "is not exist, start to create a new one"
   mv Dockerfile Dockerfile-bk
   if [ "$RHEVMIMG_NAME" == "rhevm4" ]
   then
     mv Dockerfile-rhevm4 Dockerfile
     docker build -t $RHEVMIMG_NAME .
     mv Dockerfile Dockerfile-rhevm4
   else
     mv Dockerfile-rhevm36 Dockerfile
     docker build -t $RHEVMIMG_NAME .
     mv Dockerfile Dockerfile-rhevm36
fi
mv Dockerfile-bk Dockerfile
fi

popd
