#!/bin/bash
basedir=`pwd`
case_folder="$basedir/testcases"
for layer_1 in `ls $case_folder`
do
    if [ -d $case_folder/$layer_1 ]
    then
        for layer_2 in `ls $case_folder/$layer_1`
        do
            if  [ $layer_2 == satellite ]
            then
                for layer_3 in `ls $case_folder/$layer_1/$layer_2`
                do
                    if [ -d $case_folder/$layer_1/$layer_2/$layer_3 ]
                    then
                        case_num=`ls $case_folder/$layer_1/$layer_2/$layer_3/*.py | grep -v "__init__" | wc -l`
                        echo "$layer_2/$layer_3: total $case_num"
                    fi
                done
            else
                if [ -d $case_folder/$layer_1/$layer_2 ]
                then
                    case_num=`ls $case_folder/$layer_1/$layer_2/*.py | grep -v "__init__" | wc -l`
                    echo "$layer_2: total $case_num"
                fi
            fi
        done
    fi
done