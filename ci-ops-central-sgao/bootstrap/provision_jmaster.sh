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
    --existing_nodes=*)
    EXISTING_NODES=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --ssh_user=*)
    SSH_USER=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --ssh_pass=*)
    SSH_PASS=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --name=*)
    LABEL=`echo $i | sed 's/[-a-zA-Z0-9]*=//'`
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
    --plugins=*)
    PLUGINS=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --view_label=*)
    VIEW_LABEL=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --view_filter=*)
    VIEW_FILTER=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --custom_plugins=*)
    CUSTOM_PLUGINS=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --custom_packages=*)
    CUSTOM_PACKAGES=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --custom_pymods=*)
    CUSTOM_PYMODS=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --ssl_cert=*)
    SSL_CERT=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --ssl_key=*)
    SSL_KEY=`echo $i | sed 's/[-a-zA-Z0-9_\/]*=//'`
    ;;
    --keystore_pass=*)
    KEYSTORE_PASS=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --enable_https)
    HTTPS_ENABLED=True
    ;;
    --jenkins_user=*)
    JENKINS_USER=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --api_token=*)
    API_TOKEN=`echo $i | sed 's/[-a-zA-Z0-9_]*=//'`
    ;;
    --adduuid)
    ADDUUID=True
    ;;
    --disable_jobs)
    JOBS_ENABLED=False
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
    --topology <path/to/file> (relative to --workspace) - ex. ci-ops-central/project/config/aio_jmaster
    --ssh_keyfile <path to keyfile> (relative to --workspace) - ex. ci-ops-projex/config/keys/ci-ops-central [REQUIRED]
    --existing_nodes - ips or DNS names of existing systems
    --ssh_user - different username then root [default = root]
    --ssh_pass - different password then 123456 [default = 123456]
    --name <prefix name of test resources> - ex. ci-ops
    -r|--resources_file <path/to/file> - ex. resources.json
    -a|adduuid Add a Unique identifier to name of Jenkins Master
    --workspace /path/to/workspace - ex. /var/lib/jenkins - default=`pwd`
    --plugins To include in the installation - options: plugins_base, plugins_visual, plugins_extra, plugins_all
      [default = plugins_all]
    --view_label - label for default results view (requires plugins = plugins_visual|plugins_all)  [default = Results Dashboard]
    --view_filter - RegEx used to filter jobs in default results view  (requires plugins = plugins_visual|plugins_all)  [default = .*]
    --custom_plugins - comma-separated list of additional Jenkins plugins to be installed
    --custom_packages - comma-separated list of additional RPM packages to be installed
    --custom_pymods - comma-separated list of additional Python modules to be installed via PIP
    --disable_jobs - Disable Jenkins jobs when installed
    --enable_https - Configure Jenkins to use HTTPS
    --ssl_cert - EngOps signed x509 SSL certificate to use when configuring SSL/HTTPS support for Jenkins (self-signed cert will be created if one is not specified)
    --ssl_key - SSL key provided by EngOps used to generate SSL certificate
    --keystore_pass - keystore password for Jenkins SSL keystore [default = changeme]
    --jenkins_user - Jenkins admin user (required to modify existing masters with global security enabled)
    --api_token - API token for the Jenkins admin user (required to modify existing masters with global security enabled)
    --cleanup cleanup option to pass to taskrunner
    "
    exit 0;
fi

# project_defaults,
# ssh_keyfile
# must be defined to be aware of tenant resources
if [ "$PROJECT_DEFAULTS" == "" ] ; then
   echo "Error: --project_defaults not specified exiting..." >&2; exit 1;
fi

if [ "$SSH_KEYFILE" == "" ] ; then
   echo "Error: --ssh_keyfile not specified exiting..." >&2; exit 1;
fi

if [ "$EXISTING_NODES" == "" ] && [ "$JENKINS_USER" != "" -o "$API_TOKEN" != "" ]; then
   echo "Error: --jenkins_user and --api_token can only be used with --existing_nodes exiting..." >&2; exit 1;
fi

if [ "$EXISTING_NODES" == "" ] && [ "$SSL_CERT" != "" -o "$SSL_KEY" != "" -o "$KEYSTORE_PASS" != "" ]; then
   echo "Error: --ssl_cert, --ssl_key, and --keystore_pass can only be used with --existing_nodes exiting..." >&2; exit 1;
fi

if [ "$HTTPS_ENABLED" == "" ] && [ "$SSL_CERT" != "" -o "$SSL_KEY" != "" -o "$KEYSTORE_PASS" != "" ]; then
   echo "Error: --ssl_cert, --ssl_key, and --keystore_pass can only be used with --enable_https exiting..." >&2; exit 1;
fi

if [ "$SSL_CERT" != "" ] && [ "$SSL_KEY" == "" ]; then
   echo "Error: --ssl_cert requires --ssl_key be specified exiting..." >&2; exit 1;
fi

if [ "$SSL_KEY" != "" ] && [ "$SSL_CERT" == "" ]; then
   echo "Error: --ssl_key requires --ssl_cert be specified exiting..." >&2; exit 1;
fi


# Set some defaults if values not assigned
export UUID=$(uuidgen)

if [ "$SITE" == "" ]; then SITE=qeos; fi
if [ "$WORKSPACE" == "" ]; then WORKSPACE=`pwd`; fi
if [ "$LABEL" == "" ]; then LABEL=ci-ops; fi
if [ "$TOPOLOGY" == "" ]; then TOPOLOGY=ci-ops-central/project/config/aio_jmaster; fi
if [ "$CLEANUP" == "" ]; then CLEANUP=on_failure; fi
if [ "$PLUGINS" == "" ]; then PLUGINS=plugins_all; fi
if [ "$VIEW_LABEL" == "" ]; then VIEW_LABEL="Results Dashboard"; fi
if [ "$VIEW_FILTER" == "" ]; then VIEW_FILTER=".*"; fi
if [ "$CUSTOM_PLUGINS" == "" ]; then CUSTOM_PLUGINS=''; fi
if [ "$CUSTOM_PACKAGES" == "" ]; then CUSTOM_PACKAGES=''; fi
if [ "$CUSTOM_PYMODS" == "" ]; then CUSTOM_PYMODS=''; fi
if [ "$EXISTING_NODES" == "" ]; then EXISTING_NODES=''; fi
if [ "$SSH_USER" == "" ]; then SSH_USER=root; fi
if [ "$SSH_PASS" == "" ]; then SSH_PASS=123456; fi
if [ "$SSL_CERT" == "" ]; then SSL_CERT=''; fi
if [ "$SSL_KEY" == "" ]; then SSL_KEY=''; fi
if [ "$KEYSTORE_PASS" == "" ]; then KEYSTORE_PASS='changeme'; fi
if [ "$JENKINS_USER" == "" ]; then JENKINS_USER=''; fi
if [ "$API_TOKEN" == "" ]; then API_TOKEN=''; fi

if [ "$JOBS_ENABLED" == "False" ]
then
    export JOBS_ENABLED=False
else
    export JOBS_ENABLED=True
fi

if [ "$HTTPS_ENABLED" == "True" ]
then
    export HTTPS_ENABLED=True
else
    export HTTPS_ENABLED=False
fi

if [ "$ADDUUID" == "True" ]
then
    export LABEL=$LABEL-$UUID
else
    export LABEL=$LABEL
fi

export NEW_JENKINS_NAME=$LABEL
export RESOURCES_FILE=$WORKSPACE/$LABEL.json
export PROJECT_DEFAULTS=$WORKSPACE/$PROJECT_DEFAULTS.json
export TOPOLOGY=$WORKSPACE/$TOPOLOGY.json
export SSH_KEYFILE=$WORKSPACE/$SSH_KEYFILE
export CLEANUP=$CLEANUP
export PLUGINS=$PLUGINS
export VIEW_LABEL=$VIEW_LABEL
export VIEW_FILTER=$VIEW_FILTER
export CUSTOM_PLUGINS=$CUSTOM_PLUGINS
export CUSTOM_PACKAGES=$CUSTOM_PACKAGES
export CUSTOM_PYMODS=$CUSTOM_PYMODS
export EXISTING_NODES=$EXISTING_NODES
export SSH_USER=$SSH_USER
export SSH_PASS=$SSH_PASS
export SSL_CERT=$SSL_CERT
export SSL_KEY=$SSL_KEY
export KEYSTORE_PASS=$KEYSTORE_PASS
export JENKINS_USER=$JENKINS_USER
export API_TOKEN=$API_TOKEN
export SKIP_UUID=True
unset UUID

echo "Provisioning Jenkins Master with the following environment"
echo "-----------------------------------------------------"
echo "SITE:                 $SITE"
echo "PROJECT_DEFAULTS:     $PROJECT_DEFAULTS"
echo "TOPOLOGY:             $TOPOLOGY"
echo "SSH_KEYFILE:          $SSH_KEYFILE"
echo "WORKSPACE:            $WORKSPACE"
echo "LABEL:                $LABEL"
echo "NEW_JENKINS_NAME      $LABEL"
echo "CLEANUP:              $CLEANUP"
echo "PLUGINS:              $PLUGINS"
echo "VIEW_LABEL:           $VIEW_LABEL"
echo "VIEW_FILTER:          $VIEW_FILTER"
echo "CUSTOM_PLUGINS:       $CUSTOM_PLUGINS"
echo "CUSTOM_PACKAGES:      $CUSTOM_PACKAGES"
echo "CUSTOM_PYMODS:        $CUSTOM_PYMODS"
echo "JOBS_ENABLED:         $JOBS_ENABLED"
echo "HTTPS_ENABLED:        $HTTPS_ENABLED"
echo "SSL_CERT:             $SSL_CERT"
echo "SSL_KEY:              $SSL_KEY"
echo "KEYSTORE_PASS:        $KEYSTORE_PASS"
if [ "$EXISTING_NODES" != "" ]
then
    echo "EXISTING_NODES:       $EXISTING_NODES"
    echo "SSH_USER:             $SSH_USER"
    echo "SSH_PASS:             $SSH_PASS"
    echo "JENKINS_USER:         $JENKINS_USER"
    echo "API_TOKEN:            $API_TOKEN"
fi

# Run taskrunner to provision test resources

export PYTHONPATH="$PYTHONPATH:$WORKSPACE/job-runner"
pushd $WORKSPACE/ci-ops-central
if [ "$EXISTING_NODES" != "" ]
then
    taskrunner -f targets/create_jmaster.py provision.mock_create_nodes create_jenkins \
    -D MockGetNodes.ssh_user=$SSH_USER -D MockGetNodes.ssh_pass=$SSH_PASS --cleanup=$CLEANUP
else
    taskrunner -f targets/create_jmaster.py provision.create_nodes create_jenkins --cleanup=$CLEANUP
fi

# Check for errors when provisioning
TR_STATUS=$?
if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Provisioning\nSTATUS: $TR_STATUS"; exit 1; fi

popd
exit 0
