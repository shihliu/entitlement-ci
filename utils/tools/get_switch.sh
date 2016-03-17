#!/bin/bash
# return switch to cross running virt-who against sam or satellite
switch_file="SWITCH.txt"
if [ ! -f "$switch_file" ]
then
    echo "true" > $switch_file
fi

switch=$(cat $switch_file)

if [ "$switch"x = "true"x ]
then
    echo "false" > $switch_file
else
    echo "true" > $switch_file
fi
