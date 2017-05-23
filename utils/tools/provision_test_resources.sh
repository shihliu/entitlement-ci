#!/bin/bash
#Provision Test Resources

#extend waiting times when provisioning in beaker 
$WORKSPACE/entitlement-ci/utils/tools/extend_beaker_waiting.sh

if [ "$RHEL_COMPOSE" != "" ]
then
    #reuse for multy job
    #sed -i "s/url_compose/$RHEL_COMPOSE/" $WORKSPACE/entitlement-ci/config/{topology}.json
    sed -i -e "s/url_compose/$RHEL_COMPOSE/" -e "s/os_arch/$OS_ARCH/" -e "s/os_variant/$OS_VARIANT/" $WORKSPACE/entitlement-ci/config/{topology}.json
    #check compose alread available in beaker
    chmod 777 $WORKSPACE/entitlement-ci/utils/tools/check_beaker_distro_ready.sh; . $WORKSPACE/entitlement-ci/utils/tools/check_beaker_distro_ready.sh $RHEL_COMPOSE
    #provision 5 times max if failed
    for i in `seq 5`
    do
        $WORKSPACE/ci-ops-central/bootstrap/provision_resources.sh --site=$SITE --project_defaults={project_defaults} \
        --topology={topology_path}/{topology} --ssh_keyfile={beaker_keyfile} --name={project}
        TR_STATUS=$?
        files=$(ls $WORKSPACE/*.slave 2>/dev/null)
        if [ -e "$files" ]
        then
            cat $WORKSPACE/*.slave >> $WORKSPACE/RESOURCES.txt
        fi
        if [ "$TR_STATUS" == 0 ]
        then
            break
        else
            echo "ERROR: Provisioning account $i, STATUS: $TR_STATUS"
        fi
        if [ $i -eq 5 ]
        then
            #fail and exit if provison 5 times
            echo "ERROR: provision failed after 5 times, job will be terminated..."; exit 1
        fi
    done
else
    echo "ERROR: RHEL_COMPOSE not provided, job will be terminated..."; exit 1
fi