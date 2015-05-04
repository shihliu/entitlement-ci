#!/bin/bash

# Parse command line arguments
for i in "$@"
do
case $i in
    --site=*)
    SITE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --project_defaults=*)
    PROJECT_DEFAULTS=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --topology=*)
    TOPOLOGY=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --name=*)
    NAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --bkr_jobid=*)
    BKR_JOBID=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --workspace=*)
    WORKSPACE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --help)
    HELP=True
    ;;
    *)
    echo "Unknown option $i"        # unknown option
    HELP=True
    ;;
esac
done

# Help and usage
if [ "$HELP" == "True" ]
then
    echo -e "$0
    --site <Openstack site instance>
    --project_defaults <path/to/file> - ex. ci-ops-projex/config/project_defaults [REQUIRED]
    --topology <path/to/file> - ex. ci-ops-projex/config/aio [REQUIRED]
    --name <name of resources> - ex. ci-ops-123456
    --bkr_jobid <Beaker Job ID that you want to cancel> - ex. J:666777
    --workspace /path/to/workspace - ex. /var/lib/jenkins - default=`pwd`
    "
    exit 0;
fi

# If you want to spcify a beaker job_id instead of using a env var
if [ "$BKR_JOBID" != "" ]; then export BKR_JOBID=$BKR_JOBID; fi


# project_defaults,
# topology
# must be defined to be aware of tenant resources
if [ "$PROJECT_DEFAULTS" == "" ] ; then
   echo "Error: --project_defaults not specified exiting..." >&2; exit 1;
fi

if [ "$TOPOLOGY" == "" ] ; then
   echo "Error: --topology not specified exiting..." >&2; exit 1;
fi

# Set some defaults if values not assigned and exports
if [ "$SITE" == "" ]; then SITE=qeos; fi
if [ "$WORKSPACE" == "" ]; then WORKSPACE=`pwd`; fi
if [ "$NAME" != "" ]; then
    export NAME=$NAME
    export LABEL=$NAME
elif [ "$NAME" == "" ] && [ "$UUID" == "" ]; then
    if [ -f $WORKSPACE/RESOURCES.txt ]; then
        UUID=$( grep 'UUID=' $WORKSPACE/RESOURCES.txt | cut -d'=' -f2 )
        if [ "$UUID" != "" ]; then
            export UUID=$UUID
        fi
    fi
fi

export PROJECT_DEFAULTS=$WORKSPACE/$PROJECT_DEFAULTS.json
export TOPOLOGY=$WORKSPACE/$TOPOLOGY.json
export UUID=$UUID
export SKIP_UUID=True

echo "Current Teardown environment"
echo "-----------------------------------"
echo "SITE:             $SITE"
echo "PROJECT_DEFAULTS: $PROJECT_DEFAULTS"
echo "TOPOLOGY:         $TOPOLOGY"
echo "WORKSPACE:        $WORKSPACE"
echo "LABEL:            $LABEL"
echo "UUID:             $UUID"


export PYTHONPATH="$PYTHONPATH:$WORKSPACE/job-runner"
pushd $WORKSPACE/ci-ops-central

# Teardown test resources based on the $LABEL
taskrunner -f targets/provision.py provision.provision_pipeline --cleanup=pronto

# Check for errors when tearing down resources
TR_STATUS=$?
if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Teardown\nSTATUS: $TR_STATUS"; exit 1; fi

popd

exit 0