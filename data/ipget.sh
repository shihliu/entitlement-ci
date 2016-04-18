#!/bin/sh
# return kvm guest ip by mac address
# need network bridge well configured

mac=$1
if [[ -z $mac ]]; then
   echo "mac address is null."
   exit 1
fi

if ! rpm -qa |grep nmap ;then
   echo "need nmap rpmball installed."
   exit 1
fi

if [ `uname -r | awk -F "el" '{print substr($2,1,1)}'` -ge 7 ]; then
   local_hostip=`ifconfig  | grep 'inet ' | grep -v '127.0.0.1' | grep -v '192.168' | awk '{ print $2 }'`
   ipaddr=`ip route |grep switch | grep $local_hostip | awk {'print $1'}`
elif [ `uname -r | awk -F "el" '{print substr($2,1,1)}'` -eq 6 ]; then
   local_hostip=`ifconfig  | grep 'inet ' | grep -v '127.0.0.1' | grep -v '192.168' | awk '{ print $2 }' | awk -F ":" '{ print $2 }'`
   ipaddr=`ip route |grep switch | grep $local_hostip | awk {'print $1'}`
else
   ipaddr=`ip route |grep switch |sed -n 1p|awk {'print $1'}`
fi

if [[ -n $ipaddr ]]; then
   output=$(nmap -sP -n $ipaddr | grep -i -B 2 $mac)
   if [[ -n $output ]]; then
      hostip=$(echo $output | sed -e 's/.* \([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*\).*/\1/')
   else
      echo "can not get ip by mac: $mac"
   fi
else
   echo "no scanner port found"
fi

echo $hostip
