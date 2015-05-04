#!/bin/bash

# Parse command line arguments
for i in "$@"
do
case $i in
    --name=*)
    NAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --remote_user=*)
    REMOTE_USER=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --playbooks=*)
    ANSIBLEPLAYBOOKS=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    -p|--pattern=*)
    PATTERN=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --ssh_keyfile=*)
    SSH_KEYFILE=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --hostsfile=*)
    HOSTSFILE=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    -r|--resources_output=*)
    RESOURCES_OUTPUT=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --users=*)
    USERS=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --runlocal=*)
    RUNLOCAL=False
    ;;
    --useips)
    USEIPS=True
    ;;
    --workspace=*)
    WORKSPACE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --cleanup=*)
    CLEANUP=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
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
    --name <Ansible Execution Name> - ex. Ansible-Exec
    --remote_user remote user to execute ansible on the host - default = root
    --playbooks Comma separated list to the relative path of each playbook [REQUIRED]
    --pattern Pattern to use in the /etc/ansible/hosts-<UUID> file - default = root,test
    --ssh_keyfile <path to keyfile> (relative to $WORKSPACE) - ex. ci-ops-projex/config/keys/ci-ops-central [REQUIRED]
    --hostsfile Full path to the file that will contain the necesary hosts from RESOURCES_OUTPUT - default = /etc/ansible/hosts-<UUID>
    -r|--resources_output <path/to/file> (relative to $WORKSPACE) - default = $WORKSPACE/RESOURCES.txt
    --users Possible usernames on the system to perform commans as - default = root,test
    --runlocal Add the local attribute to the /etc/ansible/hosts-<UUID> for some hosts - default = False
    --useips Convert hostnames to ips and use that in the /etc/ansible/hosts-<UUID> - default = True
    --workspace /path/to/workspace - ex. /var/lib/jenkins - default=`pwd`
    --cleanup cleanup option to pass to taskrunner - default = always
    "
    exit 0;
fi

# playbooks
# ssh_keyfile
# must be defined to be aware of tenant resources
if [ "$ANSIBLEPLAYBOOKS" == "" ] ; then
   echo "Error: --playbooks not specified exiting..." >&2; exit 1;
fi

if [ "$SSH_KEYFILE" == "" ] ; then
   echo "Error: --ssh_keyfile not specified exiting..." >&2; exit 1;
fi

# Set some defaults if values not assigned
export UUID=$(uuidgen)

if [ "$NAME" == "" ]; then NAME=Ansible-Exec; fi
if [ "$REMOTE_USER" == "" ]; then REMOTE_USER=root; fi
if [ "$PATTERN" == "" ]; then PATTERN=testsystems; fi
if [ "$HOSTSFILE" == "" ]; then HOSTSFILE=hosts-$UUID; fi
if [ "$USERS" == "" ]; then USERS=root,test; fi
if [ "$RUNLOCAL" == "" ]; then RUNLOCAL=False; fi
if [ "$USEIPS" == "" ]; then USEIPS=True; fi
if [ "$RESOURCES_OUTPUT" == "" ]; then RESOURCES_OUTPUT=RESOURCES.txt; fi
if [ "$WORKSPACE" == "" ]; then WORKSPACE=`pwd`; fi
if [ "$CLEANUP" == "" ]; then CLEANUP=always; fi

export NAME=$NAME
export REMOTE_USER=$REMOTE_USER
export PATTERN=$PATTERN
export USERS=$USERS
export RUNLOCAL=$RUNLOCAL
export USEIPS=$USEIPS
export WORKSPACE=$WORKSPACE
export HOSTSFILE=$WORKSPACE/$HOSTSFILE
export RESOURCES_OUTPUT=$WORKSPACE/$RESOURCES_OUTPUT
export ANSIBLEPLAYBOOKS=$ANSIBLEPLAYBOOKS
export SSH_KEYFILE=$WORKSPACE/$SSH_KEYFILE
export CLEANUP=$CLEANUP

echo "Executing Ansible playbooks with the following environment"
echo "----------------------------------------------------------"
echo "NAME:              $NAME"
echo "REMOTE_USER:       $REMOTE_USER"
echo "ANSIBLEPLAYBOOKS:  $ANSIBLEPLAYBOOKS"
echo "PATTERN:           $PATTERN"
echo "HOSTSFILE:         $HOSTSFILE"
echo "SSH_KEYFILE:       $SSH_KEYFILE"
echo "WORKSPACE:         $WORKSPACE"
echo "RESOURCES_OUTPUT:  $RESOURCES_OUTPUT"
echo "USERS:             $USERS"
echo "USEIPS:            $USEIPS"
echo "RUNLOCAL:          $RUNLOCAL"
echo "CLEANUP:           $CLEANUP"

# Run taskrunner to execute Ansible playbooks

export PYTHONPATH="$PYTHONPATH:$WORKSPACE/job-runner"
pushd $WORKSPACE/ci-ops-central
taskrunner -f targets/ansible_exec.py ansible_pipeline --cleanup=$CLEANUP

# Check for errors when executing Ansible playbooks
TR_STATUS=$?
if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Executing Ansible\nSTATUS: $TR_STATUS"; exit 1; fi

popd
exit 0

