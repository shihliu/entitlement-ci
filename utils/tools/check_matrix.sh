#!/bin/bash
# According to following matrix to run or exit testing
# SWITCH=Matrix1, run kvm/hyper-v against sam, esx/rhevm agaist satellite, xen against stage
# SWITCH=Matrix2, run kvm/hyper-v against satellite, esx/rhevm agaist stage, xen against sam
# SWITCH=Matrix3, run kvm/hyper-v against stage, esx/rhevm agaist sam, xen against satellite

if [[ "$SERVER_TYPE"x = "DEFAULT"x ]]
then
    export SERVER_TYPE=STAGE
fi

echo "SWITCH is $SWITCH, SERVER_TYPE is $SERVER_TYPE"

if [[ "$1"x = "group_a"x ]]
then
    if [[ "$SWITCH"x = ""x ]] || [[ "$SWITCH"x = "Matrix1"x && "$SERVER_TYPE"x = "SAM"x ]] || [[ "$SWITCH"x = "Matrix2"x && "$SERVER_TYPE"x = "SATELLITE"x ]] || [[ "$SWITCH"x = "Matrix3"x && "$SERVER_TYPE"x = "STAGE"x ]]
    then
        echo "Matrix check passed, continue ...";
    else
        echo "Matrix check failed, exit ..."; exit 1;
    fi
elif [[ "$1"x = "group_b"x ]]
then
    if [[ "$SWITCH"x = ""x ]] || [[ "$SWITCH"x = "Matrix1"x && "$SERVER_TYPE"x = "SATELLITE"x ]] || [[ "$SWITCH"x = "Matrix2"x && "$SERVER_TYPE"x = "STAGE"x ]] || [[ "$SWITCH"x = "Matrix3"x && "$SERVER_TYPE"x = "SAM"x ]]
    then
        echo "Matrix check passed, continue ...";
    else
        echo "Matrix check failed, exit ..."; exit 1;
    fi
elif [[ "$1"x = "group_c"x ]]
then
    if [[ "$SWITCH"x = ""x ]] || [[ "$SWITCH"x = "Matrix1"x && "$SERVER_TYPE"x = "STAGE"x ]] || [[ "$SWITCH"x = "Matrix2"x && "$SERVER_TYPE"x = "SAM"x ]] || [[ "$SWITCH"x = "Matrix3"x && "$SERVER_TYPE"x = "SATELLITE"x ]]
    then
        echo "Matrix check passed, continue ...";
    else
        echo "Matrix check failed, exit ..."; exit 1;
    fi
else
    echo "Check matrix failed, exit ..."; exit 1;
fi