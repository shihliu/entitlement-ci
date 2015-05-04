Jenkins redhat-ci-plugin
************************
The CI team has created a Jenkins plugin (redhat-ci-plugin) providing the following functionality:

1. A build trigger to submit jenkins jobs upon receipt of a matching CI message.
2. A post-build action that may be used to submit a message to the CI topic upon the completion of a job.

The build trigger part of the plugin grabs messages from the brew bus and our
own CI message bus and triggers the CI workflow based on contents of the message.
The post build action part of the plugin actually publishes messages on our
CI message bus.  The idea behind all of this is that CI is not just limited
to the interaction in Jenkins, but all tools errata, bugzilla, etc. can use
a common message bus to publish and retrieve messages.

The plugin works on a per-jenkins instance basis.

Additional redhat-ci-plugin details can be found on the following page:

    `Jenkins CI Plugin <https://mojo.redhat.com/docs/DOC-999594>`_.


Installation
============
The *redhat-ci-plugin* plugin along with *jenkins-ci-sidekick* (a python module extending Jenkins Job Builder
to configure jobs to use the redhat-ci-plugin) is installed by default when a Jenkins master is provisioned
using the ci-ops-central provision_jmaster.sh script.

.. [#] `provision_jmaster.sh Usage <jenkins.html#jenkins>`_

    or if you want to install it standalone

::

    pip install --index-url=http://ci-ops-jenkins-update-site.rhev-ci-vms.eng.rdu2.redhat.com/packages/simple jenkins-ci-sidekick

Configuring Jobs to use redhat-ci-plugin 
=========================================

Configuring the Trigger
-----------------------
To trigger on a CI post-build action a JMS selector similar to the following must be used:

  CI_TYPE = '<message-type>'

The valid values for '<message-type>' can be found in the "Type" column in the messages
table on this page:

    `Continuous Integration Messages <https://mojo.redhat.com/docs/DOC-948824>`_

The *jenkins-ci-sidekick* python module provides a means of configuring the **CI Event** build trigger
using Jenkins job builder.  A sample of the YAML is included below.

ci-trigger YAML
+++++++++++++++
::

    - job:
        triggers:
            - ci-trigger:
                jms-selector: 'CI_TYPE = ''tier-1-testing-done'''

Configuring the Publisher
-------------------------
The plugin also provides a post-build action for publishing messages to the CI topic upon job completion.
Enabling the post-build action on a job requires two additional piece of information:

1. The message type - full list of valid message types can be found in the "JJB YAML Message Type" column in the messges table at `Continuous Integration Messages <https://mojo.redhat.com/docs/DOC-948824>`_
2. The message content

The jenkins-ci-sidekick python module provides a means of configuring the **CI Notifier** post-build action
using Jenkins job builder.  A sample of the YAML is included below.

ci-publisher YAML
+++++++++++++++++
::

    -job:
        publishers:
            - ci-publisher:
                message-type: 'FunctionalTestingDone'
                message-content: 'FUNCTIONAL TESTING COMPLETE'

