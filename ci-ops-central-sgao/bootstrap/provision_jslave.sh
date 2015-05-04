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
    --jslavename=*)
    JSLAVENAME=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --jslavelabel=*)
    JSLAVELABEL=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --jslaveimage=*)
    JSLAVEIMAGE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --jslaveflavor=*)
    JSLAVEFLAVOR=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --jslave_execs=*)
    JSLAVE_EXECS=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --jswarm_ver=*)
    JSWARM_VER=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --jswarm_jar_loc=*)
    JSWARM_JAR_LOC=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    -r|--resources_file=*)
    RESOURCES_FILE=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --jenkins_master_url=*)
    JENKINS_MASTER_URL=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --jenkins_master_username=*)
    JENKINS_MASTER_USERNAME=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --jenkins_master_password=*)
    JENKINS_MASTER_PASSWORD=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --jenkins_cli=*)
    JENKINS_CLI=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --skip_cust)
    SKIP_CUST=True
    ;;
    --skip_ans)
    SKIP_ANS=True
    ;;
    --workspace=*)
    WORKSPACE=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
    ;;
    --cleanup=*)
    CLEANUP=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --jslavecreate)
    JSLAVECREATE=True
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
    --topology <path/to/file> (relative to --workspace) - ex. ci-ops-central/project/config/aio_jslave
    --ssh_keyfile <path to keyfile> (relative to --workspace) - ex. ci-ops-projex/config/keys/ci-ops-central [REQUIRED]
    --jslavename <name of Jenkins slave> - ex. ci-ops-slave - Note: Label will be the same if none specified
    --jslavelabel <label(s) for Jenkins slave> - space separated list of desired labels ex. ci-ops-slaves
    --jslaveimage <name of image used for slave> - ex. rhel-6.5_jeos
    --jslaveflavor <flavor size> - ex. m1.large
    --jslave_execs <number of executors> - ex. 10
    --jswarm_ver <version of the jswarm agent plugin> - ex. 1.22
    --jswarm_jar_loc <location of jswarm agent plugin> - ex. /root
    --jslavecreate - Create jenkins slave
    -r|--resources_file <path/to/file> - ex. resources.json
    --jenkins_master_url <url of jenkins master> - ex. http://10.3.45.100 [REQUIRED]
    --jenkins_master_username - The username used to connect to the jenkins master
    --jenkins_master_password - The password used to connect to the jenkins master
    --jenkins_cli <full path to jenkins cli> - ex. /var/cache/jenkins/war/WEB-INF/jenkins-cli.jar
    --skip_cust Don't install extra repositories
    --skip_ans Don't install ansible
    --workspace /path/to/workspace - ex. /var/lib/jenkins - default=`pwd`
    --cleanup cleanup option to pass to taskrunner
    "
    exit 0;
fi

# project_defaults,
# topology
# jenkins_master_url
# ssh_keyfile
# must be defined to be aware of tenant resources
if [ "$PROJECT_DEFAULTS" == "" ] ; then
   echo "Error: --project_defaults not specified exiting..." >&2; exit 1;
fi

if [ "$TOPOLOGY" == "" ] ; then
   echo "WARNING: --topology not specified, using default value of ci-ops-central/project/config/aio_jslave..." >&2;
   TOPOLOGY="ci-ops-central/project/config/aio_jslave"
fi

if [ "$SSH_KEYFILE" == "" ] ; then
   echo "Error: --ssh_keyfile not specified exiting..." >&2; exit 1;
fi

if [ "$JENKINS_MASTER_URL" == "" ] ; then
   echo "Error: --jenkins_master_url not and JENKINS_MASTER_URL env var empty specified exiting..." >&2; exit 1;
fi

# Set some defaults if values not assigned
re='^[0-9]+$'
if (! [[ "$JSLAVE_EXECS" =~ $re ]] || [ "$JSLAVE_EXECS" == "" ]) ; then
   echo "warning: --jslave_execs was either not a number or not provided default will be 10" >&2
   JSLAVE_EXECS=10
fi

if [ "$SITE" == "" ]; then SITE=qeos; fi
if [ "$WORKSPACE" == "" ]; then WORKSPACE=`pwd`; fi
if [ "$JSLAVENAME" == "" ]; then JSLAVENAME=ci-ops-slave; fi
if [ "$JSLAVELABEL" == "" ]; then JSLAVELABEL=$JSLAVENAME; fi
if [ "$JSLAVECREATE" == "" ]; then JSLAVECREATE=False; fi
if [ "$JSWARM_VER" == "" ]; then JSWARM_VER=1.22; fi
if [ "$JSWARM_JAR_LOC" == "" ]; then JSWARM_JAR_LOC=; fi
if [ "$RESOURCES_FILE" == "" ]; then RESOURCES_FILE=$JSLAVENAME.json; fi
if [ "$JENKINS_CLI" == "" ]; then JENKINS_CLI=/var/cache/jenkins/war/WEB-INF/jenkins-cli.jar; fi
if [ "$SKIP_CUST" == "" ]; then SKIP_CUST=False; fi
if [ "$SKIP_ANS" == "" ]; then SKIP_ANS=False; fi
if [ "$CLEANUP" == "" ]; then CLEANUP=on_failure; fi

if [ "$JSLAVEIMAGE" != "" ]; then
    export IMAGE=$JSLAVEIMAGE
fi
if [ "$JSLAVEFLAVOR" != "" ]; then
    export FLAVOR=$JSLAVEFLAVOR
fi

export WORKSPACE=$WORKSPACE
export JSLAVENAME=$JSLAVENAME
export JSLAVELABEL=$JSLAVELABEL
export JSWARM_VER=$JSWARM_VER
export JSWARM_JAR_LOC=$JSWARM_JAR_LOC
export LABEL=$JSLAVENAME
export PROJECT_DEFAULTS=$WORKSPACE/$PROJECT_DEFAULTS.json
export TOPOLOGY=$WORKSPACE/$TOPOLOGY.json
export SSH_KEYFILE=$WORKSPACE/$SSH_KEYFILE
export JSWARM_EXECS=$JSLAVE_EXECS
export COUNT=1
export RESOURCES_FILE=$WORKSPACE/$LABEL.json
export JENKINS_MASTER_URL=$JENKINS_MASTER_URL
export JENKINS_CLI=$JENKINS_CLI
export CLEANUP=$CLEANUP
export JENKINS_MASTER_USERNAME=$JENKINS_MASTER_USERNAME
export JENKINS_MASTER_PASSWORD=$JENKINS_MASTER_PASSWORD
export SKIP_CUST=$SKIP_CUST
export SKIP_ANS=$SKIP_ANS
export SKIP_UUID=True
unset UUID

echo "Provisioning with the following environment"
echo "-------------------------------------------"
echo "SITE:                 $SITE"
echo "PROJECT_DEFAULTS:     $PROJECT_DEFAULTS"
echo "TOPOLOGY:             $TOPOLOGY"
echo "SSH_KEYFILE:          $SSH_KEYFILE"
echo "WORKSPACE:            $WORKSPACE"
echo "JSLAVENAME:           $JSLAVENAME"
echo "JSLAVELABEL:          $JSLAVELABEL"
echo "LABEL:                $LABEL"
echo "JSWARM_VER:           $JSWARM_VER"
echo "JSWARM_JAR_LOC:       $JSWARM_JAR_LOC"
echo "JSLAVEIMAGE:          $JSLAVEIMAGE"
echo "JSLAVEFLAVOR:         $JSLAVEFLAVOR"
echo "JSLAVE_EXECS:         $JSLAVE_EXECS"
echo "JSLAVECREATE:         $JSLAVECREATE"
echo "SKIP_CUSTOMIZATION:   $SKIP_CUST"
echo "SKIP_ANSIBLE:         $SKIP_ANS"
echo "RESOURCES_FILE:       $RESOURCES_FILE"
echo "CLEANUP:              $CLEANUP"

# Run taskrunner to deploy a Jenkins slave if JSLAVECREATE=True and JSLAVENAME doesn't exist
if [ "$JSLAVECREATE" == "True" ]
then
    # Check if the Jenkins slave name exists or needs to be created
    echo ""
    echo "JENKINS_MASTER_URL:   $JENKINS_MASTER_URL"
    echo "JSLAVENAME:           $JSLAVENAME"
    echo "JSLAVELABEL:          $JSLAVELABEL"
    echo "JENKINS_CLI:          $JENKINS_CLI"
    echo ""

    java -jar $JENKINS_CLI -s $JENKINS_MASTER_URL -noCertificateCheck get-node $JSLAVENAME
    CHECK_NAME=`java -jar $JENKINS_CLI -s $JENKINS_MASTER_URL  -noCertificateCheck get-node $JSLAVENAME 2>/dev/null | grep description | sed 's/.*from \(.*\) :.*/\1/'`
    if [ "$CHECK_NAME" == "" ]
    then
        echo ""
        echo "Jenkins Slave name was not found"
        echo "Deploying Jenkins Slave with Name $JSLAVENAME"

        export PYTHONPATH="$PYTHONPATH:$WORKSPACE/job-runner"
        pushd $WORKSPACE/ci-ops-central
        taskrunner -f targets/setup_jslave.py provision.provision_pipeline create_jslave --cleanup=$CLEANUP

        # Check for errors when provisioning
        TR_STATUS=$?
        if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Provisioning\nSTATUS: $TR_STATUS"; exit 1; fi

        # This will setup the env vars for the jenkins slave resource
        export RESOURCES_INPUT=$RESOURCES_FILE
        export RESOURCES_OUTPUT=$WORKSPACE/$JSLAVENAME.slave

        grep 'EXISTING_NODES' $WORKSPACE/RESOURCES.txt | sed 's/EXISTING_NODES=\(.*\)/JSLAVEIP=\1/' > $RESOURCES_OUTPUT
        echo -e "JSLAVENAME=$JSLAVENAME\nJSLAVELABEL=$JSLAVELABEL" >> $RESOURCES_OUTPUT
        cat $RESOURCES_OUTPUT
        popd
    else
      echo ""
      echo "JSLAVEIP=$CHECK_NAME"
      echo -e "JSLAVENAME=$JSLAVENAME\nJSLAVELABEL=$JSLAVELABEL"
      echo "JSLAVEIP=$CHECK_NAME" > $WORKSPACE/$JSLAVENAME.slave
      echo -e "JSLAVENAME=$JSLAVENAME\nJSLAVELABEL=$JSLAVELABEL" >> $WORKSPACE/$JSLAVENAME.slave
      if [ -e "$WORKSPACE/$JSLAVENAME.json" ]
      then
        sed -i "s/ip\": \"\(.*\)\"/ip\": \"${CHECK_NAME}\"/" $WORKSPACE/$JSLAVENAME.json
      fi
    fi
else
    java -jar $JENKINS_CLI -s $JENKINS_MASTER_URL -noCertificateCheck get-node $JSLAVENAME
    CHECK_NAME=`java -jar $JENKINS_CLI -s $JENKINS_MASTER_URL -noCertificateCheck get-node $JSLAVENAME 2>/dev/null | grep description | sed 's/.*from \(.*\) :.*/\1/'`
    re='^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'
    if [[ "$CHECK_NAME" =~ $re ]]
    then
      echo ""
      echo "JSLAVEIP=$CHECK_NAME"
      echo -e "JSLAVENAME=$JSLAVENAME\nJSLAVELABEL=$JSLAVELABEL"
      echo "JSLAVEIP=$CHECK_NAME" > $WORKSPACE/$JSLAVENAME.slave
      echo -e "JSLAVENAME=$JSLAVENAME\nJSLAVELABEL=$JSLAVELABEL" >> $WORKSPACE/$JSLAVENAME.slave
      if [ -e "$WORKSPACE/$JSLAVENAME.json" ]
      then
        sed -i "s/ip\": \"\(.*\)\"/ip\": \"${CHECK_NAME}\"/" $WORKSPACE/$JSLAVENAME.json
      fi
    else
        echo "No IP found for slave name: $JSLAVENAME"
    fi
fi

exit 0

