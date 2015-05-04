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
    --endpoint=*)
    ENDPOINT=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --project=*)
    PROJECT=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --username=*)
    =`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    USERNAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --password=*)
    PASSWORD=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --cleanup_days=*)
    CLEANUP_DAYS=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --cleanup_ignore_pattern=*)
    CLEANUP_IGNORE_PATTERN=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --floating_ip_delay=*)
    FLOATING_IP_DELAY=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --floating_ip_checks=*)
    FLOATING_IP_CHECKS=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --janitor_target=*)
    JANITOR_TARGET=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --disable_vm_removal)
    REMOVE_VMS=False
    ;;
    --disable_ip_removal)
    REMOVE_IPS=False
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
    --endpoint - different OpenStack endpoint than that specified in project_defaults
    --project - different OpenStack project than that specified in project_defaults
    --username - different OpenStack username than that specified in project_defaults
    --password - different OpenStack password than that specified in project_defaults
    --disable_vm_removal - do not cleanup virtual machines
    --disable_ip_removal - do not cleanup floating IPs
    --cleanup_days - num days to pass from the time the node was created to be considered old [default=1]
    --cleanup_ignore_pattern - RegExp pattern to flag node names that should not be cleaned up [default=.*permanent.*]
    --floating_ip_delay - seconds to wait between execution of additional checks for unused floating IPs [default=180]
    --floating_ip_checks - number of times to check if a floating IP is still unused [default=3]
    --janitor_target - option to pass to taskrunner (options: cleanup | cleanup_test) [default=cleanup]
    "
    exit 0;
fi

# project_defaults,
# must be defined to be aware of tenant resources
if [ "$PROJECT_DEFAULTS" == "" ] ; then
   echo "Error: --project_defaults not specified exiting..." >&2; exit 1;
fi

# Set some defaults if values not assigned

if [ "$WORKSPACE" == "" ]; then WORKSPACE=`pwd`; fi
if [ "$JANITOR_TARGET" == "" ]; then JANITOR_TARGET=cleanup; fi

# Export environment variables
export PROJECT_DEFAULTS=$WORKSPACE/$PROJECT_DEFAULTS.json
export JANITOR_TARGET=$JANITOR_TARGET

if [ "$SITE" != "" ]; then export SITE=$SITE; fi
if [ "$ENDPOINT" != "" ]; then export ENDPOINT=$ENDPOINT; fi
if [ "$PROJECT" != "" ]; then export PROJECT=$PROJECT; fi
if [ "$USERNAME" != "" ]; then export USERNAME=$USERNAME; fi
if [ "$PASSWORD" != "" ]; then export PASSWORD=$PASSWORD; fi
if [ "$CLEANUP_DAYS" != "" ]; then export CLEANUP_DAYS=$CLEANUP_DAYS; fi

if [ "$CLEANUP_IGNORE_PATTERN" != "" ]; then
    export CLEANUP_IGNORE_PATTERN=$CLEANUP_IGNORE_PATTERN
fi

if [ "$FLOATING_IP_DELAY" != "" ]; then
    export FLOATING_IP_DELAY=$FLOATING_IP_DELAY
fi

if [ "$FLOATING_IP_CHECKS" != "" ]; then
    export FLOATING_IP_CHECKS=$FLOATING_IP_CHECKS
fi

if [ "$REMOVE_VMS" == "False" ]
then
    export REMOVE_VMS=False
else
    export REMOVE_VMS=True
fi

if [ "$REMOVE_IPS" == "False" ]
then
    export REMOVE_IPS=False
else
    export REMOVE_IPS=True
fi

echo "Running OpenStack Janitor with the following environment"
echo "--------------------------------------------------------"
echo "SITE:                     $SITE"
echo "PROJECT_DEFAULTS:         $PROJECT_DEFAULTS"
echo "WORKSPACE:                $WORKSPACE"
echo "JANITOR_TARGET:           $JANITOR_TARGET"
echo "ENDPOINT:                 $ENDPOINT"
echo "PROJECT:                  $PROJECT"
echo "USERNAME:                 $USERNAME"
echo "PASSWORD:                 $PASSWORD"
echo "CLEANUP_DAYS:             $CLEANUP_DAYS"
echo "CLEANUP_IGNORE_PATTERN:   $CLEANUP_IGNORE_PATTERN"
echo "FLOATING_IP_DELAY:        $FLOATING_IP_DELAY"
echo "FLOATING_IP_CHECKS:       $FLOATING_IP_CHECKS"
echo "REMOVE_VMS:               $REMOVE_VMS"
echo "REMOVE_IPS:               $REMOVE_IPS"

# Run taskrunner to provision test resources

export PYTHONPATH="$PYTHONPATH:$WORKSPACE/job-runner"
pushd $WORKSPACE/ci-ops-central
taskrunner --no-timestamp -f targets/janitor.py $JANITOR_TARGET

# Check for errors when provisioning
TR_STATUS=$?
if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Running OpenStack Janitor\nSTATUS: $TR_STATUS"; exit 1; fi

popd
exit 0
