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
if [ "$IMAGE_NAME" == "" ]; then IMAGE_NAME="rhel73"; fi
if [ "$RHEVMIMG_NAME" == "" ] 
then
    if [[ "$RHEL_COMPOSE" == "release" ]]
    then
	    #if [[ "$VIRTWHO_SRC" =~ "rhel7" ]] || [[ "$VIRTWHO_SRC" =~ "default" ]]
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
CONTAINER_NAME=$RHEVMIMG_NAME".redhat.com"

# Wait for rhevm img ready
export loop_time=1
while [ $loop_time -le 1000 ]
do
  docker images|grep $RHEVMIMG_NAME
  if [ $? -eq 0 ]
  then
    echo $RHEVMIMG_NAME " is exist."
    break
  else
    echo $RHEVMIMG_NAME "is not exist, need to wait...."
    loop_time=`expr $loop_time + 1`
    sleep 60s
    echo "loop_time is "$loop_time
  fi
done

# Create rhevm container
docker ps -a|grep $CONTAINER_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
	echo $CONTAINER_NAME "is exist!needn't to delete it"
   # Get CONTAINER'S IP		
   #docker stop $CONTAINER_NAME
   #docker rm $CONTAINER_NAME
	if [[ "$RHEL_COMPOSE" == "release" ]]
	then
		if [[ "$VIRTWHO_SRC" =~ "rhel6" ]]
		then
			RHEVM_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`        
		else
			RHEVM_IP=`docker exec -i $CONTAINER_NAME ifconfig eth1 | grep "inet "|awk '{print $2}'` 
		fi
	elif [[ "$RHEL_COMPOSE" =~ "RHEL-7" ]]
	then 
		RHEVM_IP=`docker exec -i $CONTAINER_NAME ifconfig eth1 | grep "inet "|awk '{print $2}'` 
	else 
		RHEVM_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`
	fi
	if [[ "$RHEVM_IP" == "" ]]
	then
		docker stop $CONTAINER_NAME
		docker start $CONTAINER_NAME
		pipework br0 $CONTAINER_NAME dhclient
		RHEVM_IP=`docker exec -i $CONTAINER_NAME ifconfig eth1 | grep "inet "|awk '{print $2}'` 
else
   echo "begin to create new rhevm contaner"
   echo EXIST_RHEVM=FALSE>>$WORKSPACE/ISEXISTRHEVM.txt
   if [[ "$RHEL_COMPOSE" == "release" ]]
   then
       if [[ "$VIRTWHO_SRC" =~ "rhel7" ]]
	   then
	       docker run --privileged -itd -v /sys/fs/cgroup:/sys/fs/cgroup --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEVMIMG_NAME /usr/sbin/init
           pipework br0  $CONTAINER_NAME  dhclient
           docker exec -i $CONTAINER_NAME ifconfig
           RHEVM_IP=`docker exec -i $CONTAINER_NAME ifconfig eth1 | grep "inet "|awk '{print $2}'` 
	   else
	       docker run --privileged -itd --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEVMIMG_NAME bash
           pipework br0  $CONTAINER_NAME  dhclient
           RHEVM_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`        
	   fi
   elif [[ "$RHEL_COMPOSE" =~ "RHEL-7" ]]
   then 
       docker run --privileged -itd -v /sys/fs/cgroup:/sys/fs/cgroup --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEVMIMG_NAME /usr/sbin/init
       pipework br0  $CONTAINER_NAME  dhclient
       docker exec -i $CONTAINER_NAME ifconfig
       RHEVM_IP=`docker exec -i $CONTAINER_NAME ifconfig eth1 | grep "inet "|awk '{print $2}'` 
   else 
	   docker run --privileged -itd --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEVMIMG_NAME bash
       pipework br0  $CONTAINER_NAME  dhclient
       RHEVM_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`
   fi
fi

echo "WORKSPACE is" $WORKSPACE
echo RHEVM_IP=$RHEVM_IP>>$WORKSPACE/RESOURCES.txt
echo RHEVM_HOSTNAME=$CONTAINER_NAME>>$WORKSPACE/RESOURCES.txt
echo REMOTE_IP=$RHEVM_IP>>$WORKSPACE/RESOURCES.txt
echo REMOTE_HOSTNAME=$CONTAINER_NAME>>$WORKSPACE/RESOURCES.txt
echo "WORKSPACE/RESOURCES.txt is as the following"
cat $WORKSPACE/RESOURCES.txt

echo "Provisioning with the following environment"
echo "-------------------------------------------"
echo "SITE:                     $SITE"

if [ "$RESOURCES_DIR" != "" ]; then
   export RESOURCES_OUTPUT=$RESOURCES_DIR/RESOURCES.txt
else
   export RESOURCES_OUTPUT=$WORKSPACE/RESOURCES.txt
fi
cat $RESOURCES_OUTPUT
