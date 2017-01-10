#!/bin/bash
source_folder="/var/lib/jenkins/jobs"
target_folder="/jenkins-results/reports"

if [ -d $source_folder ]
then
    if [ -d $target_folder ]
    then
        for job in `ls $source_folder | grep -E '(^virt-who|^rhsm)'-.*-runtest`
        do
            if [ ! -d $target_folder/$job ]
            then
                mkdir $target_folder/$job
            fi
            for build in `find $source_folder/$job/builds/ -maxdepth 1 -mindepth 1 -type d -printf "%f\n"`
            do
                if [ ! -d $target_folder/$job/builds/$build* ]
                then
                    # if build not exist, create folder and copy (junitResult.xml, build.xml, archive/RUNTIME_INFO.txt, archive/nosetests.xml), else do nothing
                    echo "migrated $target_folder/$job/builds/$build/"
                    mkdir -p $target_folder/$job/builds/$build/
                    cp $source_folder/$job/builds/$build/junitResult.xml $source_folder/$job/builds/$build/build.xml $source_folder/$job/builds/$build/archive/RUNTIME_INFO.txt $source_folder/$job/builds/$build/archive/nosetests.xml $target_folder/$job/builds/$build/
                fi
            done
        done
    else
        echo "target folder: $target_folder not exist"
    fi
else
    echo "source folder: $source_folder not exist"
fi