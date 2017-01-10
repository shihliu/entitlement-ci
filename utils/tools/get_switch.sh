#!/bin/bash
# return switch to cross running virt-who against sam or satellite or stage
switch_file="SWITCH.txt"
if [ ! -f "$switch_file" ]
then
    echo "Matrix1" > $switch_file
fi

switch=$(cat $switch_file)

if [ "$switch"x = "Matrix1"x ]
then
    echo "Matrix2" > $switch_file
elif [ "$switch"x = "Matrix2"x ]
then
    echo "Matrix3" > $switch_file
elif [ "$switch"x = "Matrix3"x ]
then
    echo "Matrix1" > $switch_file
fi

switch=$(cat $switch_file)