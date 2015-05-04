Jenkins
*******
The provision_jmaster.sh script can be used to:

1) `Configure a Jenkins master on an existing system <#option-1-deploy-a-jenkins-master-on-an-existing-system>`_.
2) `Provision a new Jenkins master <#option-2-deploy-a-vm-in-openstack-and-setup-a-jenkins-master>`_.


Background Information
======================

Script Usage - provision_jmaster.sh --help:
-------------------------------------------
::

    ci-ops-central/bootstrap/provision_jmaster.sh
        --site <Openstack site instance> ex. os1 or qeos
        --project_defaults <path/to/file> (relative to --workspace) - ex. ci-ops-projex/config/project_defaults [REQUIRED]
        --topology <path/to/file> (relative to --workspace) - [default =  ci-ops-central/project/config/aio_jmaster]
        --ssh_keyfile <path to keyfile> (relative to --workspace) - ex. ci-ops-projex/config/keys/ci-ops-central [REQUIRED]
        --name <prefix name of test resources> - ex. ci-ops
        -r|--resources_file <path/to/file> - ex. resources.json
        -a|adduuid Add a Unique identifier to name of Jenkins Master
        --workspace /path/to/workspace - ex. /var/lib/jenkins - default=/home/alivigni/src
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

Jenkins Plugins Information
---------------------------
The following sections list the required plugins included for each --plugins option
for the provision_jmaster.py script (used below).  'plugins_all' includes all
the plugins listed below.

Required plugins for the provisioner (plugins_base)
+++++++++++++++++++++++++++++++++++++++++++++++++++
::

    'git', 'xunit', 'ansicolor', 'multiple-scms', 'rebuild',
    'ws-cleanup', 'gerrit-trigger', 'parameterized-trigger',
    'envinject', 'email-ext', 'sonar', 'copyartifact',
    'timestamper', 'build-timeout', 'jobConfigHistory',
    'test-stability', 'jenkins-multijob-plugin',
    'dynamicparameter', 'swarm', 'shiningpanda',
    'scm-api', 'ownership', 'mask-passwords', 'role-strategy',
    'thinBackup'

Recommended plugins for Jenkins Jobs (plugins_extra)
++++++++++++++++++++++++++++++++++++++++++++++++++++
::

     'groovy-postbuild', 'gerrit-trigger', 'jobConfigHistory',
     'buildresult-trigger', 'greenballs', 'jquery', 'jquery-ui',
     'nodelabelparameter', 'token-macro', 'disk-usage',
     'tmpcleaner', 'depgraph-view', 'sonargraph-plugin',
     'throttle-concurrents', 'toolenv',
     'copy-to-slave', 'scripttrigger', 'flexible-publish',
     'PrioritySorter', 'python', 'redhat-ci-plugin',
     'credentials-binding', 'update-sites-manager'

Visual plugins for Jenkins Jobs (plugins_visual)
++++++++++++++++++++++++++++++++++++++++++++++++
::

    'ColumnPack-plugin', 'ColumnsPlugin', 'build-node-column',
    'build-view-column', 'built-on-column', 'compact-columns',
    'build-pipeline-plugin', 'configure-job-column-plugin',
    'console-column-plugin', 'console-tail', 'cron_column',
    'description-column-plugin', 'email-ext-recipients-column',
    'extra-columns', 'jobtype-column', 'nodenamecolumn',
    'progress-bar-column-plugin', 'project-stats-plugin',
    'schedule-build-plugin', 'nested-view','sectioned-view'

Requirements for Results Views
------------------------------
Sample results views are configured by the Jenkins Master provisioning script.  These views display results data for all the jobs registered in Jenkins.
The view label and regular expression jobs filter can be configured when provisioning the Jenkins master using the --view_label and --view_filter flags, respectively.

**NOTE:** The display of results data in the results views requires the following:

1. The Jenkins Master must have the visual plugins installed (via plugins_visual or plugins_all).
2. The results views require that the Jenkins jobs being displayed are configured to publish JUnit or XUnit test result reports.


Configuring a Jenkins Master
============================

Option 1: Deploy a Jenkins Master on an Existing System
-------------------------------------------------------
**NOTE:** *Make sure you can ssh via root*

Option 1.1: Provisioning Jenkins on an existing RHEL6 System
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. [#] `Install and Preparation <README.html#preparation>`_.

Example: Provision Jenkins Master with all plugins and default results views (containing all jobs)
//////////////////////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes=<system ip> \
    --ssh_user=<system user> --ssh_pass=<system password> --plugins=plugins_all

Example: Provision Jenkins Master with all plugins (default) and customize results views
////////////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes=<system ip> \
    --ssh_user=<system user> --ssh_pass=<system password> --view_label="ci-ops-projex" --view_filter=".*projex.*"

Example: Provision Jenkins Master with plugins_extra (results views will not be configured)
///////////////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes=<system ip> \
    --ssh_user=<system user> --ssh_pass=<system password> --plugins=plugins_extra

Example: Provision Jenkins Master with custom plugins, packages, and Python modules
///////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes=<system ip> \
    --custom_plugins="<plugin1>" --custom_packages="<package1>,<package2>" --custom_pymods="<module1>,<module2>,<module3>" \
    --ssh_user=<system user> --ssh_pass=<system password> --view_label="ci-ops-projex" --view_filter=".*projex.*"

Example: Provision Jenkins Master with HTTPS (self-signed cert) and customize results views
///////////////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes=<system ip> \
    --ssh_user=<system user> --ssh_pass=<system password> --view_label="ci-ops-projex" --view_filter=".*projex.*" \
    --enable_https


Option 1.2: Using a pre-existing Jenkins Master
+++++++++++++++++++++++++++++++++++++++++++++++

.. [#] `Install and Preparation <README.html#preparation>`_.

Example: Configure Jenkins Master with all plugins and default results views (containing all jobs)
//////////////////////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes=<system ip> \
    --ssh_user=<system user> --ssh_pass=<system password> --plugins=plugins_all

Example: Configure Jenkins Master with plugins_base(views will not be configured)
/////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes=<system ip> \
    --ssh_user=<system user> --ssh_pass=<system password> --plugins=plugins_base

Example: Configure Jenkins Master already configured with needed Required plugins to have customized results views
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes=<system ip> \
    --ssh_user=<system user> --ssh_pass=<system password> --plugins=plugins_visual --view_label="RHEL" --view_filter=".*RHEL[67].*"

**NOTE:** *The command above can be run multiple times to create results views/tabs with different labels and filters.*

Example: Configure Jenkins Master additional plugins, packages, and Python modules to Jenkins Master
////////////////////////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes=<system ip> \
    --custom_plugins="<plugin1>,<plugin2>,<plugin3>" --custom_packages="<package1>" --custom_pymods="<module1>,<module2>" \
    --ssh_user=<system user> --ssh_pass=<system password> --view_label="ci-ops-projex" --view_filter=".*projex.*"

Example: Configure Jenkins Master (with global security enabled) with HTTPS (EngOps signed cert)
//////////////////////////////////////////////////////////////////////////////////////////////////////////
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --plugins=plugins_all \
    --existing_nodes=<system ip> --ssh_user=<system user> --ssh_pass=<system password> --enable_https \
    --ssl_cert=<path to cert> --ssl_key=<SSL key> --keystore_pass=<password> --jenkins_user=<jenkins admin user> \
    --api_token=<jenkins admin API token>


Option 2: Deploy a VM in Openstack and setup a Jenkins Master
-------------------------------------------------------------

.. [#] `Install and Preparation <README.html#preparation>`_.
.. [#] `Setup a project_defaults.json file <README.html#setup-a-project-defaults-json-file>`_.

Example: Provisioning a Jenkins Master (with default views)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --plugins=plugins_all --cleanup=on_failure

Example: Provisioning a Jenkins Master with customized views and HTTPS (self-signed cert)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --plugins=plugins_all --view_label="ci-ops-projex" \
    --view_filter=".*projex.*" --enable_https --cleanup=on_failure

**NOTE:** *The provision_jmaster.sh script can be run multiple times to create results views/tabs with different labels and filters.
See Option 1.2 above for an example.*

Example: Provisioning a Jenkins Master with custom packages, plugins, and Python modules
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --plugins=plugins_all --custom_plugins="<plugin1>,<plugin2>" \
    --custom_packages="<package1>,<package2>,<package3>" --custom_pymods="<module1>,<module2>" --cleanup=on_failure


Updating the Configuration on Multiple Jenkins Masters
======================================================
The provision_jmaster.sh script allows you to specify a comma-separated list of existing nodes (IPs) to be configured.
For example, the following command would add a dashboard view labeled RHEL to the three nodes listed (assumes all
three nodes have the same ssh_user and ssh_pass configured):
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --existing_nodes="<system ip1>,<system ip2>,<system ip3>" \
    --ssh_user=<system user> --ssh_pass=<system password> --plugins=plugins_all --view_label="RHEL" --view_filter=".*RHEL[67].*"

**NOTE:** There is a limitation when running provision_jmaster.sh on existing nodes that have Jenkins global security enabled.
The script will only work when you specify a single existing node since a Jenkins API token is required and the API
token is tied to that specific Jenkins master.  If there is a desire to update multiple nodes (with global security enabled) at once
or to manage jobs on a set of nodes with mixed security configurations (i.e. a mix of security enabled/disabled), see
Dealing with Jenkins Security below.

Dealing with Jenkins Security
-----------------------------
If there is a desire to update the configuration on multiple Jenkins masters that have global security enabled or to manage the jobs on
a set of nodes with mixed security configurations (i.e. a mix of security enabled/disabled), you can use a simple wrapper script
to automate the execution of provision_jmaster.sh on the nodes.  In its simplest form, it could look something like this.

Create a input file containing  a comma-separated list of needed data:
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
::

    [jflynn@jflynn workspace]$ cat jenkins.in
    10.8.53.55,jenkinsuser,4b2ab3ceb7dfbf0fca61ed95172dcb9e
    10.8.49.75,testuser,ee67754c6e031057cd1e379bd0ec3193
    10.8.48.94,,

**NOTE:** Above, the user name and API token are left blank if global security is not enabled on the given master IP.

**NOTE:** If additional data like ssl certificates and keys are needed, you would need to add these to your data, as well.

Feed the input file into a simple shell script similar to the following:
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
::

    [jflynn@jflynn workspace]$ cat update_jenkins.sh
    #!/bin/bash

    while IFS=, read ip user token; do
        echo $ip $user $token
        ci-ops-central/bootstrap/provision_jmaster.sh \
            --project_defaults=ci-ops-projex/config/project_defaults_qe \
            --ssh_keyfile=ci-ops-projex/config/keys/ci-ops-central \
            --existing_nodes="$ip" --view_label="aio" \
            --view_filter=".*aio.*" --jenkins_user=$user --api_token=$token
    done < jenkins.in

