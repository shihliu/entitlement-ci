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
    --ssh_keyfile=*)
    SSH_KEYFILE=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --name=*)
    NAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --image=*)
    IMAGE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    -r|--resources_file=*)
    RESOURCES_FILE=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --workspace=*)
    WORKSPACE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --cleanup=*)
    CLEANUP=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    -s|--skipuuid)
    SKIP_UUID=True
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
    --project_defaults <path/to/file> (relative to --workspace) - ex. ci-ops-projex/config/project_defaults [REQUIRED]
    --topology <path/to/file> (relative to --workspace) - ex. ci-ops-projex/config/aio [REQUIRED]
    --ssh_keyfile <path to keyfile> (relative to --workspace) - ex. ci-ops-projex/config/keys/ci-ops-central [REQUIRED]
    --name <prefix name of test resources, override topology name> - ex. ci-ops
    --image <override image name for openstack in topology file> - ex. rhel6-5_jeos
    -r|--resources_file <path/to/file> - ex. resources.json
    -s|--skipuuid Don't add UUID for a unique identifier in the name
    --workspace /path/to/workspace - ex. /var/lib/jenkins - default=`pwd`
    --cleanup cleanup option to pass to taskrunner
    "
    exit 0;
fi

# project_defaults,
# topology
# ssh_keyfile
# must be defined to be aware of tenant resources
if [ "$PROJECT_DEFAULTS" == "" ] ; then
   echo "Error: --project_defaults not specified exiting..." >&2; exit 1;
fi

if [ "$TOPOLOGY" == "" ] ; then
   echo "Error: --topology not specified exiting..." >&2; exit 1;
fi

if [ "$SSH_KEYFILE" == "" ] ; then
   echo "Error: --ssh_keyfile not specified exiting..." >&2; exit 1;
fi

# Set some defaults if values not assigned

if [ "$SITE" == "" ]; then SITE=qeos; fi
if [ "$WORKSPACE" == "" ]; then WORKSPACE=`pwd`; fi
if [ "$CLEANUP" == "" ]; then CLEANUP=on_failure; fi
if [ "$SKIP_UUID" == "" ]; then SKIP_UUID=False; fi
if [ "$SKIP_UUID" == "False" ] || [ "$SKIP_UUID" == "false" ]; then
    export UUID=$( uuidgen );
fi
if [ "$NAME" != "" ]; then
    export NAME=$NAME;
    export LABEL=$NAME'-'$UUID;
    unset UUID
fi

if [ "$IMAGE" != "" ]; then
    export IMAGE=$IMAGE
fi

export WORKSPACE=$WORKSPACE
export PROJECT_DEFAULTS=$WORKSPACE/$PROJECT_DEFAULTS.json
export TOPOLOGY=$WORKSPACE/$TOPOLOGY.json
export SSH_KEYFILE=$WORKSPACE/$SSH_KEYFILE
export SKIP_UUID=$SKIP_UUID
export CLEANUP=$CLEANUP

echo "Provisioning resources with the following environment"
echo "-----------------------------------------------------"
echo "SITE:             $SITE"
echo "PROJECT_DEFAULTS: $PROJECT_DEFAULTS"
echo "TOPOLOGY:         $TOPOLOGY"
echo "SSH_KEYFILE:      $SSH_KEYFILE"
if [ "$SKIP_UUID" == "False" ] || [ "$SKIP_UUID" == "false" ]; then
    echo "UUID:             $UUID"
fi
if [ "$IMAGE" != "" ]; then
    echo "IMAGE         $IMAGE"
fi
echo "SKIP_UUID:        $SKIP_UUID"
echo "WORKSPACE:        $WORKSPACE"
echo "LABEL:            $LABEL"
echo "CLEANUP:          $CLEANUP"

# Run taskrunner to provision test resources

export PYTHONPATH="$PYTHONPATH:$WORKSPACE/job-runner"
pushd $WORKSPACE/ci-ops-central
taskrunner -f targets/provision.py provision.provision_pipeline --cleanup=$CLEANUP

# Check for errors when provisioning
TR_STATUS=$?
if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Provisioning\nSTATUS: $TR_STATUS"; exit 1; fi

export RESOURCES_OUTPUT=$WORKSPACE/RESOURCES.txt
cat $RESOURCES_OUTPUT
popd
exit 0
