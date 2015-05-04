Running
*******


Running with Jenkins
====================

Run the install.sh from the ci-ops-central Repo
-----------------------------------------------

.. [#] `Install and Preparation <README.html#preparation>`_.

Add jenkins jobs to Jenkins using Jenkins Job Builder
-----------------------------------------------------

Create a config file for your Jenkins master instance
+++++++++++++++++++++++++++++++++++++++++++++++++++++
::

    cat > config
    [jenkins]
    user=
    password=
    url=http://<jenkins master hostname or ip>/

Update with jobs from your own product code repo
++++++++++++++++++++++++++++++++++++++++++++++++
**Note: ci-proj-ex is en example of this type of repo**
::

    jenkins-jobs --conf ./config update ci-ops-projex/jobs

You can now execute jobs directly from Jenkins

Running Standalone
==================

.. [#] `Install and Preparation <README.html#preparation>`_.

Provision Test Resources Example
--------------------------------
::

    ci-ops-central/bootstrap/provision_resources.sh --site=qeos --project_defaults=<path to project_defaults directory>/project_defaults \
    --topology=<path to topology directory>/bkr_and_os --ssh_keyfile=<path to ssh-key-file> --cleanup=on_failure

provision_resources.sh --help
-----------------------------
::

    ci-ops-central/bootstrap/provision_resources.sh
        --site <Openstack site instance>
        --project_defaults <path/to/file> (relative to --workspace) - ex. ci-ops-projex/config/project_defaults [REQUIRED]
        --topology <path/to/file> (relative to --workspace) - ex. ci-ops-projex/config/aio [REQUIRED]
        --ssh_keyfile <path to keyfile> (relative to --workspace) - ex. ci-ops-projex/config/keys/ci-ops-central [REQUIRED]
        --name <prefix name of test resources> - ex. ci-ops
        -r|--resources_file <path/to/file> - ex. resources.json
        -s|--skipuuid Don't add UUID for a unique identifier in the name
        --workspace /path/to/workspace - ex. /var/lib/jenkins - default=/home/alivigni/src
        --cleanup cleanup option to pass to taskrunner

Provision a Jenkins Slave Example
---------------------------------
::

    ci-ops-central/bootstrap/provision_jslave.sh --site=qeos --project_defaults=<path to project_defaults directory>/project_defaults \
    --topology=ci-ops-central/project/config/aio_jslave --ssh_keyfile=<path to ssh-key-file> \
    --jslavename=jslave-projex-slave --jslaveflavor=m1.large --jslaveimage=rhel-6.5_jeos \
    --jslave_execs=10 --jslavecreate --resources_file=jslave-projex-slave.json

provision_jslave.sh --help
--------------------------
::

    ci-ops-central/bootstrap/provision_jslave.sh
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
        --workspace /path/to/workspace - ex. /var/lib/jenkins - default=<current working directory>
        --cleanup cleanup option to pass to taskrunner

Provisioning a Jenkins Master Example:
--------------------------------------
::

    ci-ops-central/bootstrap/provision_jmaster.sh --project_defaults=<path to project_defaults directory>/project_defaults \
    --ssh_keyfile=<path to ssh-key-file> --name=<name of choice> --plugins=plugins_all --cleanup=on_failure

provision_jmaster.sh --help:
----------------------------
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
