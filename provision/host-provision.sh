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
fi

export PASS='red2015'

# Wait for rhel img ready
export loop_time=1
while [ $loop_time -le 100 ]
do
  docker images|grep $RHEL_IMAGE_NAME
  if [ $? -eq 0 ]
  then
    echo $RHEL_IMAGE_NAME " is exist."
    break
  else
    echo $RHEL_IMAGE_NAME "is not exist, need to wait...."
    loop_time=`expr $loop_time + 1`
    sleep 60s
    echo "loop_time is "$loop_time
  fi
done

# Create new rhel container
docker ps -a|grep $CONTAINER_NAME
isRhelExist=$?
if [ $isRhelExist -eq 0 ]
then
   echo $CONTAINER_NAME "is exist!need to delete to create new one"
   docker stop $CONTAINER_NAME
   docker rm $CONTAINER_NAME
fi
# New provision process
echo $CONTAINER_NAME "is not exist"
export time=0
export max_time=3
export REMOTE_IP=""
# Re-create container three times
while( [[ "$REMOTE_IP" == "" ]] && [[ $max_time -gt $time ]])
do
    if [[ $CONTAINER_NAME =~ "rhel7" ]] || [[ $CONTAINER_NAME =~ "RHEL-7" ]]
    then
        docker run --privileged -itd -v /sys/fs/cgroup:/sys/fs/cgroup --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEL_IMAGE_NAME /usr/sbin/init
    else
        docker run --privileged -itd --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEL_IMAGE_NAME bash
    fi
    pipework br0 $CONTAINER_NAME dhclient
    isGetIp=$?
    if [ $isGetIp -eq 0 ]
    then
       echo "success to run pipework on "$CONTAINER_NAME "pipework result is "$isGetIp
    else
       echo "failed to run pipework on "$CONTAINER_NAME "pipework result is "$isGetIp
    fi
    if [[ $CONTAINER_NAME =~ "rhel7" ]] || [[ $CONTAINER_NAME =~ "RHEL-7" ]]
    then
        docker exec -i $CONTAINER_NAME ifconfig
        REMOTE_IP=`docker exec -i $CONTAINER_NAME ifconfig eth1 | grep "inet "|awk '{print $2}'`
    else
        REMOTE_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`
    fi
    time=time+1
done
# Recreate /etc/resolve as it re-write by dhclient-script
(
cat <<EOF
search rhts.eng.pek2.redhat.com redhat.com
nameserver 10.73.2.107
nameserver 10.73.2.108
nameserver 10.66.127.10
EOF
) >/etc/resolv.conf
cat /etc/resolv.conf
# Old provision process
# if [[ $CONTAINER_NAME =~ "rhel7" ]] || [[ $CONTAINER_NAME =~ "RHEL-7" ]]
# then
#     docker run --privileged -itd -v /sys/fs/cgroup:/sys/fs/cgroup --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEL_IMAGE_NAME /usr/sbin/init
# else
#     docker run --privileged -itd --hostname $CONTAINER_NAME --name $CONTAINER_NAME --net=none $RHEL_IMAGE_NAME bash
# fi
# pipework br0 $CONTAINER_NAME dhclient
# isGetIp=$?
# if [ $isGetIp -eq 0 ]
# then
#    echo "success to run pipework on "$CONTAINER_NAME "pipework result is "$isGetIp
# else
#    echo "failed to run pipework on "$CONTAINER_NAME "pipework result is "$isGetIp
# fi
# if [[ $CONTAINER_NAME =~ "rhel7" ]] || [[ $CONTAINER_NAME =~ "RHEL-7" ]]
# then
#     docker exec -i $CONTAINER_NAME ifconfig
#     REMOTE_IP=`docker exec -i $CONTAINER_NAME ifconfig eth1 | grep "inet "|awk '{print $2}'`
# else
#     REMOTE_IP=`docker exec -i $CONTAINER_NAME /sbin/ifconfig eth1 | grep "inet addr:"| awk '{print $2}' | cut -c 6-`
# fi
echo "REMOTE_IP is "$REMOTE_IP
docker exec -i $CONTAINER_NAME hostname $CONTAINER_NAME
docker exec -i $CONTAINER_NAME hostname
docker exec -i $CONTAINER_NAME yum install -y openssh-server openssh-clients net-tools passwd
docker exec -i $CONTAINER_NAME sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
docker exec -i $CONTAINER_NAME ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
docker exec -i $CONTAINER_NAME ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
docker exec -i $CONTAINER_NAME /usr/sbin/sshd -D &
echo -e "$PASS\n$PASS" | docker exec -i $CONTAINER_NAME /usr/bin/passwd
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
