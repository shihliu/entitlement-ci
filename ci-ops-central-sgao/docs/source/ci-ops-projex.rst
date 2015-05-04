ci-ops-projex - Project Example
*******************************

Sample project repo and generated files
=======================================

If you have run the install.sh in ci-ops-central you should have the example repo.
Otherwise do the following:
::

    mkdir -p <source code directory>; cd <source code directory>
    git clone http://git.app.eng.bos.redhat.com/ci-ops-projex.git

Full Jenkins Job Builder YAML
-----------------------------
::

    - job-template:
        name: 'ci-ops-central-{project}-{topology}-1-provision'
        defaults: ci-ops-projex-provision
        node: master
        parameters:
            - choice:
                name: SITE
                choices:
                  - qeos
                  - os1
                description: |
                  Site where to provision resourcess
        builders:
            - shell: |
                #!/bin/bash

                export JSLAVENAME={jslavename}
                # Provision Jenkins Slave
                if [ "$JSLAVENAME" != "master" ]
                then
                    $WORKSPACE/ci-ops-central/bootstrap/provision_jslave.sh --site=$SITE --project_defaults={project_defaults} \
                    --topology=ci-ops-central/project/config/aio_jslave --ssh_keyfile={ssh_keyfile} \
                    --jslavename={jslavename} --jslaveflavor={jslaveflavor} --jslaveimage={jslaveimage} \
                    --jslave_execs={jslave_execs} --jslavecreate --resources_file={jslavename}.json

                    TR_STATUS=$?
                    if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Provisioning\nSTATUS: $TR_STATUS"; exit 1; fi
                fi

                # Provision Test Resources
                $WORKSPACE/ci-ops-central/bootstrap/provision_resources.sh --site=$SITE --project_defaults={project_defaults} \
                --topology={topology_path}/{topology} --ssh_keyfile={ssh_keyfile} --name={project}

                TR_STATUS=$?

                files=$(ls $WORKSPACE/*.slave 2>/dev/null)
                if [ -e "$files" ]
                then
                    cat $WORKSPACE/*.slave >> $WORKSPACE/RESOURCES.txt
                fi

                if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Provisioning\nSTATUS: $TR_STATUS"; exit 1; fi


            - inject:
                properties-file: $WORKSPACE/RESOURCES.txt

        publishers:
          - archive:
              artifacts: '*.txt, *.json'
              allow-empty: 'true'
          - trigger-parameterized-builds:
              - project: '{project}-{topology}-2-runtest'
                current-parameters: true
                condition: 'SUCCESS'
                property-file: $WORKSPACE/RESOURCES.txt
                fail-on-missing: true
              - project: 'ci-ops-central-{project}-{topology}-3-teardown'
                current-parameters: true
                condition: 'UNSTABLE_OR_WORSE'
                property-file: $WORKSPACE/RESOURCES.txt
                fail-on-missing: true

    - job-template:
        name: '{project}-{topology}-2-runtest'
        defaults: ci-ops-projex-runtest
        node: '{jslavename}'
        builders:
            - copyartifact:
                project: 'ci-ops-central-{project}-{topology}-1-provision'
                filter: '*.txt, *.json'
                target: $WORKSPACE

            - shell: |
                #!/bin/bash

                export TOPOLOGY={topology}
                {testparams}

                echo "TOPOLOGY: {topology}"

                echo "Ping Jenkins Slave"
                ping -c 15 $JSLAVEIP

                echo "Jenkins machine info we are running on"
                ifconfig

                echo "Pinging Test Resources"
                echo $EXISTING_NODES | xargs -i -d , ping -c 30 {{}}
                cat $WORKSPACE/RESOURCES.txt

        publishers:
          - archive:
              artifacts: '**/**'
              allow-empty: 'true'
          - trigger-parameterized-builds:
              - project: 'ci-ops-central-{project}-{topology}-3-teardown'
                current-parameters: true

    - job-template:
        name: 'ci-ops-central-{project}-{topology}-3-teardown'
        defaults: ci-ops-projex-provision
        node: master
        builders:
            - shell: |
                #!/bin/bash

                export JSLAVETEARDOWN={jslaveteardown}
                # Teardown Jenkins Slave
                $WORKSPACE/ci-ops-central/bootstrap/teardown_resources.sh --site=$SITE --project_defaults={project_defaults} \
                --topology={topology_path}/{topology} --name=$LABEL

                TR_STATUS=$?
                if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Teardown\nSTATUS: $TR_STATUS"; exit 1; fi

                if [ "$JSLAVETEARDOWN" == "True" ]
                then
                  $WORKSPACE/ci-ops-central/bootstrap/teardown_jslave.sh --site=$SITE --project_defaults={project_defaults} \
                  --topology=ci-ops-central/project/config/aio_jslave --jslavename=$JSLAVENAME \
                  --jslaveusername={jslaveusername} --jslavepassword={jslavepassword} --jslaveip=$JSLAVEIP --jslaveteardown

                  TR_STATUS=$?
                  if [ "$TR_STATUS" != 0 ]; then echo "ERROR: Teardown\nSTATUS: $TR_STATUS"; exit 1; fi
                fi

    - job-group:
        name: provision-runtest-teardown
        jobs:
          - 'ci-ops-central-{project}-{topology}-1-provision'
          - '{project}-{topology}-2-runtest'
          - 'ci-ops-central-{project}-{topology}-3-teardown'

    - project:
        name: ci-ops-projex-jobs
        project:
         - projex
        project_defaults:
         - ci-ops-projex/config/project_defaults
        topology_path:
         - ci-ops-projex/config
        topology:
         - aio_RHEL6-4
         - aio_RHEL6-5
         - aio_RHEL7-0
        ssh_keyfile:
         - ci-ops-projex/config/keys/ci-ops-central
        testparams:
         - echo "I am a test parameter"
        jobs:
          - provision-runtest-teardown
        jslavename:
         - jslave-projex-slave
        jslave_execs:
         - 10
        jslaveimage:
         - rhel-6.5_jeos
        jslaveflavor:
         - m1.large
        jslaveusername:
         - root
        jslavepassword:
         - 123456
        jslaveteardown:
         - False

Full Jenkins Job Builder YAML Defaults
--------------------------------------
::

    - defaults:
        name: ci-workflow-provision
        description: |
            Managed by Jenkins Job Builder. Do not edit via web.
        concurrent: true
        scm:
            - git:
                url: 'https://code.engineering.redhat.com/gerrit/ci-ops-central'
                branches:
                    - origin/master
                basedir: ci-ops-central
            - git:
                url: 'https://code.engineering.redhat.com/gerrit/ci-ops-projex'
                branches:
                    - origin/master
                basedir: ci-ops-projex
            - git:
                url: 'https://code.engineering.redhat.com/gerrit/job-runner'
                branches:
                    - origin/master
                basedir: job-runner
        wrappers:
            - default-ci-workflow-wrappers

    - defaults:
        name: ci-workflow-runtest
        description: |
            Managed by Jenkins Job Builder. Do not edit via web.
        concurrent: true
        scm:
            - git:
                url: 'http://git.app.eng.bos.redhat.com/git/ci-ops-projex.git'
                branches:
                    - origin/master
                basedir: ci-ops-projex
        wrappers:
            - default-ci-workflow-wrappers
            - default-ci-workflow-build-timeout-wrapper

    - wrapper:
        name: default-ci-workflow-wrappers
        wrappers:
            - ansicolor
            - workspace-cleanup
            - timestamps

    - wrapper:
        name: default-ci-workflow-build-timeout-wrapper
        wrappers:
            - timeout:
                timeout-var: 'BUILD_TIMEOUT'
                fail: true
                elastic-percentage: 150
                elastic-default-timeout: 90
                type: elastic

    - publisher:
        name: default-ci-workflow-publishers
        publishers:
              - email-ext:
                  recipients: $DEFAULT_RECIPIENTS
                  reply-to: $DEFAULT_REPLYTO
                  content-type: default
                  subject: $DEFAULT_SUBJECT
                  body: $DEFAULT_CONTENT
                  attach-build-log: false
                  always: true
                  unstable: true
                  first-failure: true
                  not-built: true
                  aborted: true
                  regression: true
                  failure: true
                  improvement: true
                  still-failing: true
                  success: true
                  fixed: true
                  still-unstable: true
                  pre-build: true
                  matrix-trigger: only-configurations
                  send-to:
                    - requester
                    - recipients

    - publisher:
        name: default-ci-workflow-runtest-publishers
        publishers:
               - xunit:
                   thresholdmode: 'number'
                   thresholds:
                     - failed:
                           unstable: 0
                           unstablenew: 0
                           failure: 0
                           failurenew: 0
                     - skipped:
                           unstable: 0
                           unstablenew: 0
                           failure: 0
                           failurenew: 0
                   types:
                     - junit:
                         pattern: '*.xml'
                         deleteoutput: false

project_defaults.json
---------------------
This json describes the project/tenant for the infrastructure resources

.. code-block:: json

    {
        "resources": [
            {
                "name": "ci-ops",
                "flavor": "m1.large",
                "count": "1",
                "image": "rhel-6.5_jeos"
            }
        ],
        "sites": [
            {
                "site": "qeos",
                "project": "<put project tenant name here>",
                "username": "<put project username here>",
                "password": "<put project password here",
                "keypair": "<put project keypair here",
                "networks": ["<put project networks here>"],
                "region": "",
                "foreman_url": "<Foreman URL>",
                "foreman_username": "<Foreman server username>",
                "foreman_password": "<Foreman server password>",
                "foreman_version": "1.5",
                "os_mapping_foreman": {
                            "Redhat-6": {
                                "ptable": "Kickstart default",
                                "media": "RHEL-6.x"
                            },
                            "fedora": {
                                "ptable": "Fedora17",
                                "media": "Fedora"
                            },
                            "Redhat-7": {
                                "ptable": "Fedora 16+ / GRUB2",
                                "media": "RHEL-7-rel-eng-latest"
                            }
                }
            }
        ]
    }

The job-template in the runtest2 shell section
----------------------------------------------

The key areas below to focus are the following:
::

    node: '{jslavename}'

This tag calls out the slave label and should generally fall in line with the test matrix you have chosen.
Here the matrix is composed of project and topology.

If you just want to run it on the master then make it **node: master**

The **copyartifact** and **publishers: - trigger-parameterized-builds:**
sections should generally be left alone since they pull the environment from the provisioning upstream job

::

    - job-template:
        name: '{project}-{topology}-2-runtest'
        defaults: ci-ops-projex-runtest
        node: '{jslavename}'
        builders:
            - copyartifact:
                project: 'ci-ops-central-{project}-{topology}-1-provision'
                filter: '*.txt, *.json'
                target: $WORKSPACE

            - shell: |
                #!/bin/bash

                export TOPOLOGY={topology}
                {testparams}

                echo "TOPOLOGY: {topology}"

                echo "Ping Jenkins Slave"
                ping -c 15 $JSLAVEIP

                echo "Jenkins machine info we are running on"
                ifconfig

                echo "Pinging Test Resources"
                echo $EXISTING_NODES | xargs -i -d , ping -c 30 {{}}
                cat $WORKSPACE/RESOURCES.txt

        publishers:
          - archive:
              artifacts: '**/**'
              allow-empty: 'true'
          - trigger-parameterized-builds:
              - project: 'ci-ops-central-{project}-{topology}-3-teardown'
                current-parameters: true

project section
---------------
::

    - project:
        name: ci-ops-projex-jobs
        project:
         - projex
        project_defaults:
         - ci-ops-projex/config/project_defaults
        topology_path:
         - ci-ops-projex/config
        topology:
         - aio_RHEL6-4
         - aio_RHEL6-5
         - aio_RHEL7-0
        ssh_keyfile:
         - ci-ops-projex/config/keys/ci-ops-central
        testparams:
         - echo "I am a test parameter"
        jobs:
          - provision-runtest-teardown
        jslavename:
         - jslave-projex-slave
        jslave_execs:
         - 10
        jslaveimage:
         - rhel-6.5_jeos
        jslaveflavor:
         - m1.large
        jslaveusername:
         - root
        jslavepassword:
         - 123456
        jslaveteardown:
         - False

project_defaults macro JJB YAML
+++++++++++++++++++++++++++++++
::

    project_defaults:
     - ci-ops-projex/config/project_defaults

Topology and topology_path macro JJB YAML
+++++++++++++++++++++++++++++++++++++++++
The topology macro is the same name used to call the JSON topology files below.
**ex. aio = aio.json** The topology_path is the location in the repo where it exists
::

    topology_path:
     - ci-ops-projex/config
    topology:
     - aio_RHEL6-4
     - aio_RHEL6-5
     - aio_RHEL7-0

ssh_keyfile macro JJB YAML
++++++++++++++++++++++++++
This is the macro to setup your openstack keyfile
::

    ssh_keyfile:
     - ci-ops-projex/config/keys/ci-ops-central

Jenkins Slave macro JJB YAML
++++++++++++++++++++++++++++
These macros defines the slave that will be deployed if you want to avoid deployment of a slave and want to run
on the master change jslavename to **master**
::

    jslavename:
     - jslave-projex-slave
    jslave_execs:
     - 10
    jslaveimage:
     - rhel-6.5_jeos
    jslaveflavor:
     - m1.large
    jslaveusername:
     - root
    jslavepassword:
     - 123456
    jslaveteardown:
     - False

Topology Example - Openstack
----------------------------

os1.json
++++++++

*NOTE: metadata below can be any variable(s) you want to define to be in the resulting output after provisioning*

.. code-block:: json

    {
        "resources": [
            {
                "name": "project-1",
                "count": "1",
                "flavor": "m1.medium",
                "image": "rhel-6.5_jeos",
                "metadata": {
                    "username": "fedora",
                    "key": "fedora20.pem"
                }

            }
       ]
    }

os2comp.json
++++++++++++

.. code-block:: json

    {
        "resources": [
            {
                "name": "project-rhel-6-5",
                "count": "2",
                "flavor": "m1.medium",
                "image": "rhel-6.5_jeos",
                "metadata": {
                    "username": "fedora",
                    "key": "fedora20.pem"
                }
            },
            {
                "name": "project-rhel-6-4",
                "count": "2",
                "flavor": "m1.large",
                "image": "rhel-6.4_jeos",
                "metadata": {
                    "username": "fedora-19",
                    "key": "fedora19.pem"
                }
            }
        ]
    }

Topology Example - Foreman Baremetal
------------------------------------

foreman.json
++++++++++++

.. code-block:: json

    {
        "resources": [
            {
                "name": "foreman",
                "count": "1",
                "hostnames": ["loki10.ci.lab.tlv.redhat.com"],
                "image": "rhel-6.5",
                "ssh_user": "root",
                "ssh_pass": "qum5net",
                "rebuild": "True",
                "reserve": "False",
                "metadata": {
                    "myvar": "ci-ops-central",
                    "message": "Hello World"
                }
            }
       ]
    }

foreman_hg_prefix.json
++++++++++++++++++++++

.. code-block:: json

    {
        "resources": [
            {
                "name": "foreman",
                "count": "1",
                "hostgroup": "P-RHEVM-3.4-RHEL65-HOSTS",
                "prefix": "loki"
                "image": "rhel-6.5",
                "ssh_user": "root",
                "ssh_pass": "qum5net",
                "rebuild": "True",
                "reserve": "False",
                "metadata": {
                    "myvar": "ci-ops-central",
                    "message": "Hello World"
                }
            }
       ]
    }

Topology Example - Ansible Palybooks
------------------------------------
os2-ansible.json
++++++++++++++++

.. code-block:: json

    {
        "resources": [
            {
                "name": "ci-ops-central-ans",
                "count": "2",
                "flavor": "m1.medium",
                "image": "rhel-6.5_jeos",
                "metadata": {
                    "myvar": "ci-ops-central-ans",
                    "message": "Hello World"
                },
                "ansible": {
                    "playbooks": [
                        "ci-ops-central/ansible/playbooks/ans_info_in_file_ex.yml",
                        "ci-ops-central/ansible/playbooks/ans_touch_file_ex.yml"
                    ],
                    "remote_user": "root",
                    "pattern": "testsystems"
                }
            }
       ]
    }

Topology Example - Repos and Yum and Pip Packages
-------------------------------------------------

RHEL7-1_repos.json
++++++++++++++++++

.. code-block:: json

    {
        "resources": [
            {
                "name": "ci-ops-rhel-7-1",
                "count": "1",
                "flavor": "m1.large",
                "image": "RHEL-7.1-Server-x86_64-latest",
                "repos": [
                    {
                        "name": "brew-rhpkg",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng/brew/rhel/$releasever/"
                    },
                    {
                        "name": "epel7",
                        "mirrorlist": "https://mirrors.fedoraproject.org/metalink?repo=epel-7&arch=$basearch"
                    },
                    {
                        "name": "rhel7-latest",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng/latest-RHEL-7/compose/Server/x86_64/os/"
                    },
                    {
                        "name": "rhel7-optional",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng//latest-RHEL-7/compose/Server-optional/x86_64/os/"
                    },
                    {
                        "name": "rhel7-extras",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng/latest-EXTRAS-7-RHEL-7/compose/Server/x86_64/os/"
                    },
                    {
                        "name": "RHOS-5.0",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng/OpenStack/5.0-RHEL-7/latest/RH7-RHOS-5.0/$basearch/os/"
                    }
                ]
            }
       ]
    }

RHEL7-1_repos_packages.json
+++++++++++++++++++++++++++

.. code-block:: json

    {
        "resources": [
            {
                "name": "ci-ops-rhel-7-1",
                "count": "1",
                "flavor": "m1.medium",
                "image": "RHEL-7.1-Server-x86_64-latest",
                "metadata": {
                    "myvar": "ci-ops-rhel-7-1",
                    "message": "Hello World"
                },
                "repos": [
                    {
                        "name": "brew-rhpkg",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng/brew/rhel/$releasever/"
                    },
                    {
                        "name": "epel7",
                        "mirrorlist": "https://mirrors.fedoraproject.org/metalink?repo=epel-7&arch=$basearch"
                    },
                    {
                        "name": "rhel7-latest",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng/latest-RHEL-7/compose/Server/x86_64/os/"
                    },
                    {
                        "name": "rhel7-optional",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng//latest-RHEL-7/compose/Server-optional/x86_64/os/"
                    },
                    {
                        "name": "rhel7-extras",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng/latest-EXTRAS-7-RHEL-7/compose/Server/x86_64/os/"
                    },
                    {
                        "name": "RHOS-5.0",
                        "baseurl": "http://download.lab.bos.redhat.com/rel-eng/OpenStack/5.0-RHEL-7/latest/RH7-RHOS-5.0/$basearch/os/"
                    }
                ],
                "packages": [
                    {
                        "yum":  "rhpkg git wget curl rpm-build yum-utils glibc-static golang device-mapper-devel btrfs-progs-devel sqlite-devel rpmdevtools python-tools python2-devel"
                    },
                    {
                        "pip":  "jenkins-job-builder"
                    }
                ]
            }
       ]
    }

Topology Beaker Configuration and Example
-----------------------------------------

Job Groups
++++++++++
*Note: job_group refers to a job_group within Beaker.*

+----------------------+------------------------------------------------------------+
| Beaker Group         | Beaker Username                                            |
+======================+============================================================+
| ci-ops-central       |      N/A                                                   |
+----------------------+------------------------------------------------------------+
| ci-ops-brms          | jenkins/brms-jenkins.rhev-ci-vms.eng.rdu2.redhat.com       |
+----------------------+------------------------------------------------------------+
| ci-ops-fusesource    | jenkins/fusesource-jenkins.rhev-ci-vms.eng.rdu2.redhat.com |
+----------------------+------------------------------------------------------------+
| ci-ops-kenerl-qe     | jenkins/kernel-qe-jenkins.rhev-ci-vms.eng.rdu2.redhat.com  |
+----------------------+------------------------------------------------------------+
| ci-ops-pit           | jenkins/pit-jenkins.rhev-ci-vms.eng.rdu2.redhat.com        |
+----------------------+------------------------------------------------------------+
| ci-ops-rhos-qe       | jenkins/rhos-qe-jenkins.rhev-ci-vms.eng.rdu2.redhat.com    |
+----------------------+------------------------------------------------------------+
| ci-ops-rhsos-qe      | jenkins/rhsos-jenkins.rhev-ci-vms.eng.rdu2.redhat.com      |
+----------------------+------------------------------------------------------------+
| ci-ops-rhev-ci       | jenkins/rhev-ci-jenkins.rhev-ci-vms.eng.rdu2.redhat.com    |
+----------------------+------------------------------------------------------------+

bkr_and_os.json
+++++++++++++++

.. code-block:: json

    {
        "resources": [
            {
                "metadata": {
                    "username": "someuser",
                    "key": "somekey.pem"
                },
                "recipesets": [
                    {
                        "distro": "RHEL-6.5",
                        "arch": "X86_64",
                        "keyvalue": ["MEMORY>1000", "DISKSPACE>20000"],
                        "variant": "Server",
                        "hostrequire": ["arch=X86_64"],
                        "bkr_data": {
                            "role": "Server",
                            "name": "AppServer"
                        }
                    },
                    {
                        "distro": "RHEL-6.4",
                        "arch": "X86_64",
                        "keyvalue": ["MEMORY>2000", "DISKSPACE>20000"],
                        "variant": "Workstation",
                        "hostrequire": ["arch=X86_64"],
                        "bkr_data": {
                            "role": "Client",
                            "name": "AppClient"
                        }
                    }
                ],
                "job_group": "ci-ops-central",
                "skip_max_attempts": "True",
            },
            {
                "name": "openstack-1",
                "count": "2",
                "flavor": "m1.medium",
                "image": "rhel-6.5_jeos",
                "metadata": {
                    "username": "rht",
                    "key": "rhkey.pem"
                }
            }
       ]
    }

Topology Example - Openstack with cloud-init
--------------------------------------------
*Note: Cloud-init support requires cloud-init and cloud-utils*
*You can use cloud-init scripts from your repo*

aio_cloud-init.json
+++++++++++++++++++

.. code-block:: json

    {
        "resources": [
            {
                "name": "ci-ops-central",
                "count": "1",
                "flavor": "m1.medium",
                "image": "rhel-6.5_jeos",
                "user-data-files": [
                    "ci-ops-projex/cloud-init/cloud-config-runcmds.txt",
                    "ci-ops-projex/cloud-init/cloud-shell-motd.txt"
                ],
                "metadata": {
                    "myvar": "ci-ops-central",
                    "message": "Hello World"
                }
            }
       ]
    }

Provisioner Output
------------------

<name-uuid>.json for each resource input
++++++++++++++++++++++++++++++++++++++++
*Note: metdata defined in topology files will show up here with the resource specifics*

.. code-block:: json

    {
        "resources": [
            {
                "ip": "10.8.51.78",
                "private_ip": "172.16.30.8",
                "name": "ci-prov-ex-6d1132a8-53bd-4a40-84d4-425f5b2ffb04-rs-1-1",
                "metadata": {
                    "myvar": "ci-ops-central-rs-1",
                    "message": "Hello World rs-1"
                }
            },
            {
                "ip": "10.8.51.81",
                "private_ip": "172.16.30.9",
                "name": "ci-prov-ex-6d1132a8-53bd-4a40-84d4-425f5b2ffb04-rs-1-2",
                "metadata": {
                    "myvar": "ci-ops-central-rs-1",
                    "message": "Hello World rs-1"
                }
            },
            {
                "ip": "10.8.49.194",
                "private_ip": "172.16.30.10",
                "name": "ci-prov-ex-6d1132a8-53bd-4a40-84d4-425f5b2ffb04-rs-2-1",
                "metadata": {
                    "myvar": "ci-ops-central-rs-2",
                    "message": "Hello world rs-2"
                }
            },
            {
                "ip": "10.8.48.214",
                "private_ip": "172.16.30.11",
                "name": "ci-prov-ex-6d1132a8-53bd-4a40-84d4-425f5b2ffb04-rs-2-2",
                "metadata": {
                    "myvar": "ci-ops-central-rs-2",
                    "message": "Hello world rs-2"
                }
            }
        ]
    }

resources.json
++++++++++++++
*Note: Output here has both Beaker and Openstack provisioned output*

.. code-block:: json

    {
        "resources": [
            {
                "distro": "RHEL-6.5",
                "arch": "x86_64",
                "result": "Pass",
                "family": "RedHatEnterpriseLinux6",
                "system": "intel-sugarbay-do-01.ml3.eng.bos.redhat.com"
            },
            {
                "distro": "RHEL-6.5",
                "arch": "x86_64",
                "result": "Pass",
                "family": "RedHatEnterpriseLinux6",
                "system": "phenom-01.ml3.eng.bos.redhat.com"
            },
            {
                "ip": "10.8.49.128",
                "private_ip": "172.16.30.9",
                "name": "bkr-os-test-c2fdd5c1-23c1-4c6e-b871-d1382caff338-rs-2-1"
                 "metadata": {
                    "myvar": "ci-ops-central-rs-2",
                    "message": "Hello World rs-2"
                }
            },
            {
                "ip": "10.8.49.163",
                "private_ip": "172.16.30.11",
                "name": "bkr-os-test-c2fdd5c1-23c1-4c6e-b871-d1382caff338-rs-2-2"
                 "metadata": {
                    "myvar": "ci-ops-central-rs-2",
                    "message": "Hello World rs-2"
                }
            }
        ]
    }

Jenkins Slave Resources - ex. jslave.json
+++++++++++++++++++++++++++++++++++++++++

.. code-block:: json

    {
        "resources": [
            {
                "ip": "10.8.47.111",
                "private_ip": "172.16.29.5",
                "name": "jslave-projex-aio"
            }
        ]
    }

RESOURCES.txt
+++++++++++++

*Used to inject in downstream jobs and can be referred to, but it is mainly used by ci-ops-central code base*

.. code-block:: bash

    EXISTING_NODES=10.8.51.78,10.8.51.81,10.8.49.194,10.8.48.214
    PRIVATE_IPS=172.16.30.8,172.16.30.9,172.16.30.10,172.16.30.11
    BKR_JOBID=J:
    SITE=qeos
    LABEL=ci-prov-ex-6d1132a8-53bd-4a40-84d4-425f5b2ffb04
    UUID=
    PROVISION_JOB=https://10.8.52.213/job/ci-workflow-aio_RHEL6-5-1-provision/53/
