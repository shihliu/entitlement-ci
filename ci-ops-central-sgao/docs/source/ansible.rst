Using Ansible
*************

Executing Ansible playbooks on existing resources
=================================================

This is used to execute Ansible playbooks on existing resources
::

    ci-ops-central/bootstrap/ansible_exec.sh --ssh_keyfile=ci-ops-central/targets/keys/ci-ops-central --name=ansi-test
    --playbooks=ci-ops-central/ansible/playbooks/ans_info_in_file_ex.yml,ci-ops-central/ansible/playbooks/ans_touch_file_ex.yml


Executing Ansible playbooks as part of provisioning resources
=============================================================

Keyterms for Ansible and Provisioning
-------------------------------------

* ansible - Section to indicate the execution of ansible playbooks

 - playbooks - Array of playbooks to execute
 - name - Name of ansible execution - default = "Provisioner and Ansible execution"
 - users - Users that are on the system - default = "root,test"
 - remote_user - User to run ansible playbook as - default = "root"
 - hostsfile - Ansible hosts file - default = "$WORKSPACE/hosts-<UUID>"
 - ssh_keyfile - SSH private key to talk to remote machine - default = "ci-ops-central/targets/keys/ci-ops-central"
 - pattern - Pattern of machines to execute ansible against - default = "testsystems"
 - useips - Use IPs in HOSTSFILE instead of names
 - runlocal - Run it locally from current machine


Ansible Topology file - ex. os_ansible.json
-------------------------------------------

::

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