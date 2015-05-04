Using Beaker
************

Accessing Consoles for Beaker Test Resources
============================================

When provisioning a slave using the ci-ops-central provision_jslave.sh script, kerberos and conserver packages
needed to support connecting to the Red Hat conservers will be installed on the Jenkins slave. The Master's
krb5.conf file will be copied to /etc on the slave.  In addition, the keytab file referenced in KRB_KEYTAB in
/etc/beaker/client.conf on the Master will be copied to /etc on the Jenkins slave.  This will provide the necessary
credentials and packages required to access the consoles on the Beaker test resources from the Jenkins slave.

Prerequisites
-------------

The ci-ops-central provision_jslave.sh script will configure Jenkins Slaves to support connecting to the
consoles of Beaker resources using conserver and Kerberos credentials.  The necessary Kerberos configuration
details will be copied from the Jenkins Master to the Jenkins Slave.  As such, a Jenkins Master must have the
following configuration in place:

1. *Kerberos Configuration* -- Beaker console support provided by ci-ops central requires that valid Kerberos configuration information is contained in /etc/krb5.conf on the Jenkins Master.
2. *Beaker configuration* -- /etc/beaker/client.conf must exist on the Jenkins Master, with KRB_KEYTAB pointing to a valid keytab file that exists on the Jenkins Master.

Configuring the job-template to use Beaker consoles
---------------------------------------------------
Once the slave is configured to support consoles on Beaker test resources, the runtest job-template will need to make
use of the consoles and archive the logs of the console data.  The following section will provide examples on how to
configure the runtest job to obtain the Beaker console data.  A higher-level view of the runtest job is available here:

.. [#] `The job-template in the runtest2 shell section <ci-ops-projex.html#the-job-template-in-the-runtest2-shell-section>`_.

Ensure the runtest job is designated to be run on the Slave
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
The key area to focus on here is the following:
::

    node: '{jslavename}'

This tag calls out where the job will be run.  Ensure this points to the slave label.

Capture console data while executing test
'''''''''''''''''''''''''''''''''''''''''
To capture the console data on the Beaker resources, a kinit must be performed with appropriate keytab information for your Jenkins environment.
The keytab file is copied from the Jenkins Master to /etc on the slave as part of the slave provisioning when the provision_jslave.sh script is used.

Following the kinit, you can call the console command:

console -M <conserver> <beaker_resource_hostname>

.. [#] `Additional Conserver Details <https://home.corp.redhat.com/wiki/conserver>`_

**Example of runtest shell section calling  kinit and connecting to the Beaker resource consoles:**

::

            - shell: |
                #!/bin/bash
                kinit -k -t /etc/ci-ops-jenkins.rhev-ci-vms.eng.rdu2.redhat.com.keytab jenkins/ci-ops-jenkins.rhev-ci-vms.eng.rdu2.redhat.com@REDHAT.COM

                declare -a console_pids
                pid_count=0

                #open consoles
                nodes=$(echo $EXISTING_NODES | tr "," "\n")
                for node in $nodes
                do
                    #skip nodes designated by an IP, Beaker resources are stored by hostname
                    ip_regex="^((25[0-5]|2[0-4][0-9]|[01]?[1-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[1-9][0-9]?)$"
                    if [[ $node =~ $ip_regex ]]; then
                        continue
                    fi
                    echo "Connecting to console for $node"
                    nohup console -M console.eng.bos.redhat.com $node > $WORKSPACE/$node"_console.log" &
                    console_pids[pid_count]=$!
                    pid_count+=1
                done

                #SAMPLE TEST CODE BEGIN -- REPLACE WITH YOUR TEST CODE
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
                #SAMPLE TEST CODE END -- REPLACE WITH YOUR TEST CODE

                echo "Cleaning up console processes"
                for pid in "${console_pids[@]}"
                do
                    echo "Killing console process: $pid"
                    kill -9 $pid
                done

Add build step to search for panics (OPTIONAL)
''''''''''''''''''''''''''''''''''''''''''''''
There was interest in having a means to check the Beaker console logs for panic strings.  This can be done by
adding an additional build step to the Jenkins job to search the console logs for panic strings and return a
failure code if one of these strings is found.  (NOTE: This build step should follow the one described in the
previous section.)

**Example of runtest shell section checking for panic in the console logs:**

::

            - shell: |
                #!/bin/bash

                panic_found=false
                panic_str=""

                PANIC_REGEX="Kernel panic\|Oops: \|general protection fault\|general protection handler: wrong gs\|\(XEN\) Panic"

                if stat -t $WORKSPACE/*_console.log >/dev/null 2>&1
                then
                    echo "Console logs found"
                else
                    echo "No console logs found"
                    exit 0
                fi

                logs=$(find $WORKSPACE -name "*_console.log" -print0 | xargs -0 ls)

                for log in $logs
                do
                    panic_str=`grep -e "$PANIC_REGEX" $log`

                    rc=$?

                    if [ $rc -eq 0 ]; then
                        logfilename="${log##*/}"
                        hostname=`echo $logfilename | awk -F'_' '{print $1}'`
                        echo "Panic detected on $hostname."
                        echo "Panic string found: $panic_str"
                        echo "Log file location: $JENKINS_MASTER_URL/job/$JOB_NAME/$BUILD_NUMBER/artifact/$logfilename"
                        panic_found=true
                    fi
                done

                if [ "$panic_found" = true ]; then
                    echo "Panic detected in console logs.  Marking test as FAILED."
                    exit 1
                fi

Ensure post-build action archives console log files
'''''''''''''''''''''''''''''''''''''''''''''''''''
To capture the log files, you must include a post-build action to archive the console logs in the Jenkins
job definition by ensuring files ending in ".log" (or whatever file extension you designate in your test script)
are captured.

**Examples of runtest publishers archiving the console log files:**

::

        publishers:
          - archive:
              artifacts: '**/**'
              allow-empty: 'true'

::

        publishers:
          - archive:
              artifacts: '*.txt, *.json, *.log'
              allow-empty: 'true'


Full Jenkins Job Builder YAML for runtest job-template
''''''''''''''''''''''''''''''''''''''''''''''''''''''
Putting everything described above together would result in the following YAML for the runtest job-template:

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
                kinit -k -t /etc/ci-ops-jenkins.rhev-ci-vms.eng.rdu2.redhat.com.keytab jenkins/ci-ops-jenkins.rhev-ci-vms.eng.rdu2.redhat.com@REDHAT.COM

                declare -a console_pids
                pid_count=0

                #open consoles
                nodes=$(echo $EXISTING_NODES | tr "," "\n")
                for node in $nodes
                do
                    #skip nodes designated by an IP, Beaker resources are stored by hostname
                    ip_regex="^((25[0-5]|2[0-4][0-9]|[01]?[1-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[1-9][0-9]?)$"
                    if [[ $node =~ $ip_regex ]]; then
                        continue
                    fi
                    echo "Connecting to console for $node"
                    nohup console -M console.eng.bos.redhat.com $node > $WORKSPACE/$node"_console.log" &
                    console_pids[pid_count]=$!
                    pid_count+=1
                done

                #SAMPLE TEST CODE BEGIN -- REPLACE WITH YOUR TEST CODE
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
                #SAMPLE TEST CODE END -- REPLACE WITH YOUR TEST CODE

                echo "Cleaning up console processes"
                for pid in "${console_pids[@]}"
                do
                    echo "Killing console process: $pid"
                    kill -9 $pid
                done
            - shell: |
                #!/bin/bash

                panic_found=false
                panic_str=""

                PANIC_REGEX="Kernel panic\|Oops: \|general protection fault\|general protection handler: wrong gs\|\(XEN\) Panic"

                if stat -t $WORKSPACE/*_console.log >/dev/null 2>&1
                then
                    echo "Console logs found"
                else
                    echo "No console logs found"
                    exit 0
                fi

                logs=$(find $WORKSPACE -name "*_console.log" -print0 | xargs -0 ls)

                for log in $logs
                do
                    panic_str=`grep -e "$PANIC_REGEX" $log`

                    rc=$?

                    if [ $rc -eq 0 ]; then
                        logfilename="${log##*/}"
                        hostname=`echo $logfilename | awk -F'_' '{print $1}'`
                        echo "Panic detected on $hostname."
                        echo "Panic string found: $panic_str"
                        echo "Log file location: $JENKINS_MASTER_URL/job/$JOB_NAME/$BUILD_NUMBER/artifact/$logfilename"
                        panic_found=true
                    fi
                done

                if [ "$panic_found" = true ]; then
                    echo "Panic detected in console logs.  Marking test as FAILED."
                    exit 1
                fi

        publishers:
          - archive:
              artifacts: '**/**'
              allow-empty: 'true'
          - trigger-parameterized-builds:
              - project: 'ci-ops-central-{project}-{topology}-3-teardown'
                current-parameters: true




