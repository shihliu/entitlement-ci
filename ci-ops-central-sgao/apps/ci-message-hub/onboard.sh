#!/bin/bash

BASEDIR=$(dirname $(readlink -f $0))

for jar in $BASEDIR/*.jar; do
    CLASSPATH=$CLASSPATH:$jar
done

java -cp $CLASSPATH com.redhat.ci.Onboard "$@"
