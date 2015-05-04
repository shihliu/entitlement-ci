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
    --ssh_keyfile=*)
    SSH_KEYFILE=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --existing_nodes=*)
    EXISTING_NODES=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --ssh_user=*)
    SSH_USER=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --ssh_pass=*)
    SSH_PASS=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --workspace=*)
    WORKSPACE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --update_jobs)
    UPDATE_JOBS=True
    ;;
    --jobs_repo=*)
    JOBS_REPO=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --force_update)
    FORCE_UPDATE=True
    ;;
    --enable_all)
    [ "$DISABLE_ALL_JOBS" == "True" ] && { echo "Error: Cannot specify both --enable_all and --disable_all" >&2; exit 1; }
    ENABLE_ALL_JOBS=True
    ;;
    --disable_all)
    [ "$ENABLE_ALL_JOBS" == "True" ] && { echo "Error: Cannot specify both --enable_all and --disable_all" >&2; exit 1;}
    DISABLE_ALL_JOBS=True
    ;;
    --jenkins_user=*)
    JENKINS_USER=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --api_token=*)
    API_TOKEN=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
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
    --project_defaults <path/to/file> (relative to --workspace) - [REQUIRED]
        ex. ci-ops-projex/config/project_defaults
    --workspace </path/to/workspace> - ex. /var/lib/jenkins -
        default=`pwd`
    --existing_nodes <ips> - ips or DNS names of existing systems [REQUIRED]
    --ssh_keyfile <path to keyfile> (relative to --workspace)
        ex. ci-ops-projex/config/keys/ci-ops-central
    --ssh_user <username> different username then root [default = root]
    --ssh_pass <password> different password then 123456 [default = 123456]
    --update_jobs update the Jenkins jobs on the given nodes
        --jobs_repo <repo> git repository containing yaml files with job
            definitions
            [default=git://git.app.eng.bos.redhat.com/ci-ops-projex.git]
        --force_update forcefully update Jenkins jobs; This overwrites any
            manual changes to existing jobs with data from the job repository.
    --enable_all | --disable_all Enable or Disable all Jenkins jobs. This
        overrides settings in job definitions or existing jobs.
    --jenkins_user - Jenkins admin user (required to modify existing masters with global security enabled)
    --api_token - API token for the Jenkins admin user (required to modify existing masters with global security enabled)
    "
    exit 0;
fi

# project_defaults,
# must be defined to be aware of tenant resources
if [ "$PROJECT_DEFAULTS" == "" ] ; then
   echo "Error: --project_defaults not specified.  Exiting..." >&2; exit 1;
fi

if [ "$SSH_PASS" == "" ] &&  [ "$SSH_KEYFILE" == "" ] ; then
   echo "Error: --ssh_pass or --ssh_keyfile must be specified, exiting..." >&2; exit 1;
fi

# existing_nodes must be defined
if [ "$EXISTING_NODES" == "" ] ; then
   echo "Error: --existing_nodes not specified.  Exiting..." >&2; exit 1;
fi

# check update flag dependencies
if [ "$UPDATE_JOBS" == "" -a "$JOBS_REPO" != "" ] ; then
   echo "Error: Cannot specify --jobs_repo without --update_jobs. Exiting..." >&2; exit 1;
fi

if [ "$UPDATE_JOBS" == "" -a "$FORCE_UPDATE" == "True" ] ; then
   echo "Error: Cannot specify --force_update without --update_jobs. Exiting..." >&2; exit 1;
fi


# Set some defaults if values not assigned
if [ "$SITE" == "" ]; then SITE=qeos; fi
if [ "$WORKSPACE" == "" ]; then WORKSPACE=`pwd`; fi
if [ "$SSH_USER" == "" ]; then SSH_USER=root; fi
if [ "$SSH_PASS" == "" ]; then SSH_PASS=123456; fi
if [ "$JOBS_REPO" == "" ]; then JOBS_REPO='git://git.app.eng.bos.redhat.com/ci-ops-projex.git'; fi
if [ "$ENABLE_ALL_JOBS" == "" ]; then ENABLE_ALL_JOBS=False; fi
if [ "$DISABLE_ALL_JOBS" == "" ]; then DISABLE_ALL_JOBS=False; fi
if [ "$JENKINS_USER" == "" ]; then JENKINS_USER=''; fi
if [ "$API_TOKEN" == "" ]; then API_TOKEN=''; fi

if [ "$UPDATE_JOBS" == "True" ]
then
    export UPDATE_JOBS=True
else
    export UPDATE_JOBS=False
fi

if [ "$FORCE_UPDATE" == "True" ]
then
    export FORCE_UPDATE=True
else
    export FORCE_UPDATE=False
fi

if [ "$SSH_KEYFILE" != "" ]; then
    export SSH_KEYFILE=$WORKSPACE/$SSH_KEYFILE
fi

export PROJECT_DEFAULTS=$WORKSPACE/$PROJECT_DEFAULTS.json
export EXISTING_NODES=$EXISTING_NODES
export SSH_USER=$SSH_USER
export SSH_PASS=$SSH_PASS
export JOBS_REPO=$JOBS_REPO
export ENABLE_ALL_JOBS=$ENABLE_ALL_JOBS
export DISABLE_ALL_JOBS=$DISABLE_ALL_JOBS
export JENKINS_USER=$JENKINS_USER
export API_TOKEN=$API_TOKEN

echo "Updating Jenkins Master with the following environment"
echo "-----------------------------------------------------"
echo "SITE:                 $SITE"
echo "PROJECT_DEFAULTS:     $PROJECT_DEFAULTS"
echo "SSH_KEYFILE:          $SSH_KEYFILE"
echo "WORKSPACE:            $WORKSPACE"
echo "UPDATE_JOBS:          $UPDATE_JOBS"
echo "JOBS_REPO:            $JOBS_REPO"
echo "FORCE_UPDATE          $FORCE_UPDATE"
echo "ENABLE_ALL_JOBS:      $ENABLE_ALL_JOBS"
echo "DISABLE_ALL_JOBS:     $DISABLE_ALL_JOBS"
if [ "$EXISTING_NODES" != "" ]
then
    echo "EXISTING_NODES:       $EXISTING_NODES"
    echo "SSH_USER:             $SSH_USER"
    echo "SSH_PASS:             $SSH_PASS"
    echo "JENKINS_USER:         $JENKINS_USER"
    echo "API_TOKEN:            $API_TOKEN"
fi

# Run taskrunner to manage jenkins jobs

export PYTHONPATH="$PYTHONPATH:$WORKSPACE/job-runner"
pushd $WORKSPACE/ci-ops-central

if [ "$SSH_KEYFILE" != "" ]
then
    taskrunner -f targets/job_manager.py mock_create_nodes manage_jobs \
    -D MockGetNodes.ssh_keyfile=$SSH_KEYFILE
else
    taskrunner -f targets/job_manager.py mock_create_nodes manage_jobs \
    -D MockGetNodes.ssh_user=$SSH_USER -D MockGetNodes.ssh_pass=$SSH_PASS
fi

# Check for errors when managing jobs
TR_STATUS=$?
if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Managing Jenkins Jobs\nSTATUS: $TR_STATUS"; exit 1; fi

popd
exit 0

