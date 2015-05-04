Using Restraint
***************

Execute Beaker Tasks using the Restraint test harness
=====================================================

Environment Variables
---------------------

In your Jenkins Job the following environment variables are important.
Some are setup and defaulted for you the one required is JOBXML:
::

    WORKSPACE -        In Jenkins this is already default of where you run
                       the job from or your current working directory if not on
                       Jenkins
                       DEFAULT PROVIDED - $PWD

    JOBXML -           Required points to the full path of our beaker XML
                       ex. $WORKSPACE/sandbox/platform/restraint/nfs-utils.xml
                       NO DEFAULT PROVIDED

    RESOURCES_OUTPUT - defaults to RESOURCES.txt that gets generated from the
                       provision job
                       DEFAULT PROVIDED - $WORKSPACE/RESOURCES.txt

    HOSTSFILE        - File where Jenkins slave and test resources get setup
                       DEFAULT PROVIDED - $WORKSPACE/hosts-<UUID>

    SSH_KEYFILE      - SSH Private key to talk to Jenkins slave and test
                       resources
                       DEFAULT PROVIDED - ci-ops-central/targets/keys/ci-ops-central

    REMOTE_USER      - User to ssh to system as
                       DEFAULT PROVIDED - root

    USEIPS           - Use IPs instead of names to communicate
                       DEFAULT PROVIDED - True

    RUNLOCAL         - Run locally on current machine typically the Jenkins
                       slave.  This adds local indication in the HOSTSFILE
                       DEFAULT PROVIDED - True

    PATTERN          - Pattern of machines to execute commands on
                       DEFAULT PROVIDED - testsystems

    RESTRAINTREPO    - URL to use for the restraint repo
                       DEFAULT PROVIDED - http://bpeck.fedorapeople.org/restraint/el6.repo


Jenkins Build Shell and general execution
-----------------------------------------

You can have this in the shell section of the Jenkins Build Step Shell
or you could run this from the command line.
::

    taskrunner -f $WORKSPACE/ci-ops-central/targets/restraint.py restraint_pipeline

*Note: taskrunner is required to be installed which can be done via pip*
       *pip install taskrunner*