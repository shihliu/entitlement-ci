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
    --jslavename=*)
    JSLAVENAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --jslaveusername=*)
    JSLAVEUSERNAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --jslavepassword=*)
    JSLAVEPASSWORD=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --ssh_keyfile=*)
    SSH_KEYFILE=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --jslaveip=*)
    JSLAVEIP=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --workspace=*)
    WORKSPACE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --jslaveteardown)
    JSLAVETEARDOWN=True
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
    --topology <path/to/file> - ex. ci-ops-central/project/config/aio_jslave
    --jslavename <name of Jenkins slave> - ex. ci-ops-slave  - Note: Label will be the same
    --ssh_keyfile <path to keyfile> - ex. ci-ops-projex/config/keys/ci-ops-central
    --jslaveusername <username of the jenkins slave> - ex. root
    --jslavepassword <password of the jenkins slave> - ex. 123456
    --jslaveip <ip of slave> - ex. 10.3.4.4
    --jslaveteardown - Teardown jenkins slave
    --workspace /path/to/workspace - ex. /var/lib/jenkins - default=`pwd`
    "
    exit 0;
fi

# project_defaults
# topology
# jslavename
# jslaveusername
# jslavepassword
# jslaveip
# topology
# must be defined to be aware of tenant resources
if [ "$PROJECT_DEFAULTS" == "" ] ; then
   echo "Error: --project_defaults not specified exiting..." >&2; exit 1;
fi

if [ "$TOPOLOGY" == "" ] ; then
    echo "WARNING: --topology not specified, using default value of ci-ops-central/project/config/aio_jslave..." >&2;
    TOPOLOGY="ci-ops-central/project/config/aio_jslave"
fi

if [ "$JSLAVENAME" == "" ] ; then
   echo "Error: --jslavename not specified exiting..." >&2; exit 1;
fi

if [ "$JSLAVEUSERNAME" == "" ] ; then
   echo "Error: --jslaveusername not specified exiting..." >&2; exit 1;
fi

if [ "$JSLAVEPASSWORD" == "" ] &&  [ "$SSH_KEYFILE" == "" ] ; then
   echo "Error: --jslavepassword or --ssh_keyfile must be specified, exiting..." >&2; exit 1;
fi

if [ "$JSLAVEIP" == "" ] ; then
   echo "Error: --jslaveip not specified exiting..." >&2; exit 1;
fi

# Set some defaults if values not assigned
if [ "$SITE" == "" ]; then SITE=qeos; fi
if [ "$WORKSPACE" == "" ]; then WORKSPACE=`pwd`; fi
if [ "$JSLAVETEARDOWN" == "" ]; then JSLAVETEARDOWN=False; fi

if [ -f $WORKSPACE/RESOURCES.txt ]; then
    JSLAVELABEL=$( grep 'JSLAVELABEL=' $WORKSPACE/RESOURCES.txt | cut -d'=' -f2 )
fi
if [ "$JSLAVELABEL" == "" ]; then JSLAVELABEL=$JSLAVENAME; fi


export PROJECT_DEFAULTS=$WORKSPACE/$PROJECT_DEFAULTS.json
export TOPOLOGY=$WORKSPACE/$TOPOLOGY.json
export JSLAVENAME=$JSLAVENAME
export JSLAVELABEL=$JSLAVELABEL
export LABEL=$JSLAVENAME
export EXISTING_NODES=$JSLAVEIP
export SKIP_UUID=True

echo "Current Teardown environment"
echo "-----------------------------------"
echo "SITE:             $SITE"
echo "PROJECT_DEFAULTS: $PROJECT_DEFAULTS"
echo "TOPOLOGY:         $TOPOLOGY"
echo "WORKSPACE:        $WORKSPACE"
echo "JSLAVENAME:       $JSLAVENAME"
echo "JSLAVELABEL:      $JSLAVELABEL"
echo "LABEL:            $LABEL"
echo "SSH_KEYFILE:      $SSH_KEYFILE"
echo "JSLAVEIP:         $JSLAVEIP"
echo "JSLAVEUSERNAME:   $JSLAVEUSERNAME"
echo "JSLAVEPASSWORD:   $JSLAVEPASSWORD"
echo "JSLAVETEARDOWN:   $JSLAVETEARDOWN"

# Run taskrunner to teardown a Jenkins slave if JSLAVETEARDOWN=True
if [ "$JSLAVETEARDOWN" == "True" ]
then
    echo ""
    echo "Teardown JSLAVE_NAME:  $JSLAVENAME"
    echo "Teardown JSLAVE_LABEL: $JSLAVELABEL"
    echo "Teardown JSLAVE IP:    $JSLAVEIP"
    echo ""

    export PYTHONPATH="$PYTHONPATH:$WORKSPACE/job-runner"
    pushd $WORKSPACE/ci-ops-central

    echo "Kill the Jenkins swarm plugin and teardown the Jenkins Slave"
    if [ "$SSH_KEYFILE" == "" ] ; then
        taskrunner -f targets/setup_jslave.py provision.mock_create_nodes teardown_jslave -D MockGetNodes.ssh_user=$JSLAVEUSERNAME -D MockGetNodes.ssh_pass=$JSLAVEPASSWORD
    else
        taskrunner -f targets/setup_jslave.py provision.mock_create_nodes teardown_jslave -D MockGetNodes.ssh_user=$JSLAVEUSERNAME -D MockGetNodes.ssh_keyfile=$WORKSPACE/$SSH_KEYFILE
    fi

    # Check for errors when tearing down resources
    TR_STATUS=$?
    if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Teardown\nSTATUS: $TR_STATUS"; exit 1; fi

    taskrunner -f targets/provision.py provision.create_nodes --cleanup=pronto

    # Check for errors when tearing down resources
    TR_STATUS=$?
    if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Teardown\nSTATUS: $TR_STATUS"; exit 1; fi
    popd
else
    echo "Not tearing down the slave with name $JSLAVENAME and IP $JSLAVEIP because teardown not set"
fi

exit 0

