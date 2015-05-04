#!/bin/bash

OIFS=$IFS;
IFS=",";
topsArray=($TOPOLOGIES)


if [ "$SITE" == "" ]; then SITE=qeos; fi
if [ "$WORKSPACE" == "" ]; then WORKSPACE=`pwd`; fi
if [ "$CLEANUP" == "" ]; then CLEANUP=always; fi
if [ "$PROJECT" == "" ]; then PROJECT='ci-ops-central'; fi
if [ "$TOPOLOGY_PATH" == "" ]; then TOPOLOGY_PATH='ci-ops-projex/config'; fi
if [ "$PROJECT_DEFAULTS" == "" ]; then PROJECT_DEFAULTS="$PROJECT/project/config/project_defaults"; fi
if [ "$JENKINS_MASTER_URL" == "" ]; then JENKINS_MASTER_URL=http://ci-ops-jenkins.rhev-ci-vms.eng.rdu2.redhat.com/; fi

export PROJECT_DEFAULTS=$PROJECT_DEFAULTS
export JENKINS_MASTER_URL=$JENKINS_MASTER_URL

echo "Testing ci-ops-central/ci-opsprojex code with the following environment"
echo "-----------------------------------------------------------------------"
echo "SITE:                 $SITE"
echo "PROJECT:              $PROJECT"
echo "PROJECT_DEFAULTS:     $PROJECT_DEFAULTS"
echo "TOPOLOGY_PATH:        $TOPOLOGY_PATH"
echo "TOPOLOGIES:           $TOPOLOGIES"
echo "WORKSPACE:            $WORKSPACE"
echo "CLEANUP:              $CLEANUP"
echo "JENKINS_MASTER_URL:   $JENKINS_MASTER_URL"

export UUID=$(uuidgen)

echo ""
echo "-------------------- START OF TESTING -----------------------"
for ((i=0; i<${#topsArray[@]}; ++i));
do
    export LABEL=ci-ops-test-$UUID-${topsArray[$i]}
    echo "LABEL: $LABEL"
    export TOPOLOGY=$TOPOLOGY_PATH/${topsArray[$i]}
    echo "TEST TOPOLOGY - $TOPOLOGY";
    export PYTHONPATH="$PYTHONPATH:$WORKSPACE/job-runner"
    if [ "`echo $TOPOLOGY | grep 'aio_jslave'`" != "" ]
    then
        echo "--========== Test of Jenkins Slave Provisioning ==========--"
	    ci-ops-central/bootstrap/provision_jslave.sh --site=qeos --project_defaults=$PROJECT_DEFAULTS \
	    --topology=$TOPOLOGY --ssh_keyfile=ci-ops-projex/config/keys/ci-ops-central \
	    --jslavename=$LABEL --jslavecreate --cleanup=$CLEANUP
	    # Check for errors when provisioning
        TR_STATUS=$?
        if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Testing\nSTATUS: $TR_STATUS"; exit 1; fi
    elif [ "`echo $TOPOLOGY | grep 'aio_jmaster'`" != "" ]
    then
        echo "--========== Test of Jenkins Master Provisioning ==========--"
	    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=$PROJECT_DEFAULTS \
	    --topology=$TOPOLOGY --ssh_keyfile=ci-ops-projex/config/keys/ci-ops-central \
	    --view_label=ci-ops-projex --view_filter=".*projex.*" --name=$LABEL --enable_https --cleanup=$CLEANUP
        # Check for errors when provisioning
        TR_STATUS=$?
        if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Testing\nSTATUS: $TR_STATUS"; exit 1; fi
    else
        echo "--========== Test of Test Resource Provisioning ==========--"
	    ci-ops-central/bootstrap/provision_resources.sh --site=qeos --project_defaults=$PROJECT_DEFAULTS \
	    --topology=$TOPOLOGY --ssh_keyfile=ci-ops-projex/config/keys/ci-ops-central --name=$LABEL --cleanup=$CLEANUP

        # Check for errors when provisioning
        TR_STATUS=$?
        if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Testing\nSTATUS: $TR_STATUS"; exit 1; fi
    fi
done
echo ""
echo "-------------------- END OF TESTING -----------------------"


IFS=$OIFS;
