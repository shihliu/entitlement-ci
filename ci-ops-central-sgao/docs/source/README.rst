How do I get started?
*********************

The easiest way get started is to checkout the repo below and run the install
script this should set you up with everything you need.

Preparation
===========

First, create/enter a folder where you'll have the ci-ops-central repository
and its dependencies checked out, then clone it.
::

    mkdir -p <source code directory>; cd <source code directory>
    git clone http://git.app.eng.bos.redhat.com/git/ci-ops-central.git


Next, we install the the necessary dependencies for the ci-ops-central tools. Some of them
are other git repositories, some are yum install packages. Root/sudo access is required to run this script.

Running as root user
::

    cd ci-ops-central
    ./install.sh

Running as sudo user
::

    cd ci-ops-central
    sudo ./install.sh

Setup a project_defaults.json file
==================================

This what points to your Openstack tenant project and foreman server credentials/options.
This should ultimately live in your own product repository

.. code-block:: json

    {
        "resources": [
                    {
                "name": "openstack-1",
                "count": "1",
                "flavor": "m1.medium",
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
                "foreman_url": "<put foreman url here>",
                "foreman_username": "<put foreman username here>",
                "foreman_password": "<put foreman username here>",
                "foreman_version": "1.5",
                "os_mapping_foreman": {
                            "RedHat-6": {
                                "ptable": "Kickstart default",
                                "media": "RHEL-6.x"
                            },
                            "fedora": {
                                "ptable": "Fedora17",
                                "media": "Fedora"
                            },
                            "RedHat-7": {
                                "ptable": "Fedora 16+ / GRUB2",
                                "media": "RHEL-7-rel-eng-latest"
                            }
                }
            }
        ]
    }

Setup of Topologies
===================

This is what defines what will get provisioned either in Openstack, Beaker, or Foreman.

Openstack Topology file - ex. os.json
-------------------------------------

This is an Openstack example:

.. code-block:: json

    {
        "resources": [
            {
                "name": "ci-ops-rhel-7-0",
                "count": "1",
                "flavor": "m1.medium",
                "image": "RHEL-7.0-Server-x86_64-released",
                "metadata": {
                    "myvar": "ci-ops-rhel-7-0",
                    "message": "Hello World"
                }
            }
       ]
    }

Ansible Topology file - ex. os_ansible.json
-------------------------------------------

This is an Openstack and Ansible playbook example:

.. code-block:: json

    {
        "resources": [
            {
                "name": "ci-ops-central",
                "count": "2",
                "flavor": "m1.medium",
                "image": "rhel-6.5_jeos",
                "metadata": {
                    "myvar": "ci-ops-central",
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

Beaker and Openstack Topology file - ex. bkr_and_os.json
--------------------------------------------------------

This is a Beaker and Openstack example:

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
                        "keyvalue": ["DISKSPACE>=20000"],
                        "variant": "Server",
                        "hostrequire": ["arch=X86_64", "memory>=1000"],
                        "bkr_data": {
                            "role": "Server",
                            "name": "AppServer"
                        }
                    },
                    {
                        "distro": "RHEL-6.4",
                        "arch": "X86_64",
                        "keyvalue": ["DISKSPACE>=20000"],
                        "variant": "Workstation",
                        "hostrequire": ["arch=X86_64", "memory>=1000"],
                        "bkr_data": {
                            "role": "Client",
                            "name": "AppClient"
                        }
                    }
                ],
                "job_group": "ci-ops-central"
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

Foreman Topology file - ex. foreman.json
----------------------------------------

This is a Foreman example:

.. code-block:: json

    {
        "resources": [
            {
                "name": "foreman",
                "count": "1",
                "hostnames": ["zeus-vds2.qa.lab.tlv.redhat.com"],
                "image": "rhel-6.5",
                "ssh_user": "root",
                "ssh_pass": "pass",
                "rebuild": "True",
                "reserve": "False",
                "metadata": {
                    "myvar": "ci-ops-central",
                    "message": "Hello World"
                }
            }
       ]
    }

Repos and packages - ex. RHEL7-1_repos_packages.json
----------------------------------------------------

This is a Repos and Packages example:

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

Provision resources
===================

Now that this in place you are ready to provision resources.

*Note: Paths specified for --project_defaults, --topology, and --ssh_keyfile should be relative to WORKSPACE (`pwd` or whatever you specify with --workspace).*

*Note: You don't need json on the end of the project_defaults and topology filenames.*

*Note: ssh-key-file has to be one that is already setup in the Openstack project tenant for that user.*

::


    cd <directory above where the ci-ops-central repo is>

    ci-ops-central/bootstrap/provision_resources.sh --site=qeos --project_defaults=<path to project_defaults directory>/project_defaults \
    --topology=<path to topology directory>/bkr_and_os --ssh_keyfile=<path to ssh-key-file> --cleanup=on_failure
