#!/bin/sh
# return kvm guest ip by mac address
# need network bridge well configured

mac=$1
if [[ -z $mac ]]; then
   echo "mac address is null."
   exit 1
fi

if ! rpm -qa |grep -q nmap ;then
   echo "need nmap rpmball installed."
   exit 1
fi

if [ `uname -r | awk -F "el" '{print substr($2,1,1)}'` -ge 7 ]; then
   local_hostip=`hostname -i`
   ipaddr=`ip route |grep "10.66" | grep $local_hostip | awk {'print $1'}`
else
   ipaddr=`ip route |grep "10.66" |sed -n 1p|awk {'print $1'}`
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
