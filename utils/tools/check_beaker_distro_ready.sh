#!/bin/bash
MAX_COUNT=60
for i in `seq $MAX_COUNT`
do
    bkr distros-list --name=$1
    result=$?
    if [ "$result" -eq 0 ]
    then
        echo "beaker distro $1 is ready, begin provision ..."
        exit 0
    elif [ $i -eq $MAX_COUNT ]
    then
        echo "beaker distro $1 still not ready, failed to provision ..."
        exit 1
    else
        echo "beaker distro $1 not ready yet, wait 5 minutes ..."
        sleep 300
    fi
done