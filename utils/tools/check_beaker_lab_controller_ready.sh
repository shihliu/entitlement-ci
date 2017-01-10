#!/bin/bash
# when provision beaker machines in eng office, make sure Lab Controller lab-01.rhts.eng.pek2.redhat.com is ready

MAX_COUNT=96
for i in `seq $MAX_COUNT`
do
    bkr distro-trees-list --name $1 | grep "lab-01.rhts.eng.pek2.redhat.com"
    result=$?
    if [ "$result" -eq 0 ]
    then
        echo "beaker Lab Controller lab-01.rhts.eng.pek2.redhat.com is ready, begin provision ..."
        exit 0
    elif [ $i -eq $MAX_COUNT ]
    then
        echo "beaker Lab Controller lab-01.rhts.eng.pek2.redhat.com still not ready, failed to provision ..."
        exit 1
    else
        echo "beaker Lab Controller lab-01.rhts.eng.pek2.redhat.com not ready yet, wait 1 hour ..."
        sleep 3600
    fi
done