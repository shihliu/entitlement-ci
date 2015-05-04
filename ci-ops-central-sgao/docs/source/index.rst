.. ci-ops-central documentation master file, created by
   sphinx-quickstart on Sun Jun  8 23:28:03 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ci-ops-central's code documentation!
===============================================

ci-ops-central is integration code to assist with the central continuous integration workflow/process.
This is heavily tied to the use of the Jenkins continuous integration and delivery tool.  The code is used to provision
virtualized or baremetal resources (Beaker/Foreman).

Features:
---------
* Provisioning in the following:

 - Openstack with cloud-init support
 - Baremetal - Beaker
 - Baremetal - Foreman

* Dynamic provisioning of a Jenkins slaves
* Jenkins Master provisioning and installation
* Provisioning of test resources
* All resources returned to next Jenkins job as a resources.json or RESOURCES.txt environment variables
* All topologies and project defaults can be defined in own product project repository and used to setup resources
* You can run inside or outside of Jenkins
* ci-ops-projex is an example project that shows how a project repository would be setup
* Ansible playbook support for customization of Jenkins slaves and test resources

Contents:
---------

.. toctree::
   :maxdepth: 3

   README
   overview
   running
   jenkins
   ci-trigger
   ci-ops-projex
   beaker
   restraint
   ansible


References
==========
.. [#] `Jenkins Job Builder <http://ci.openstack.org/jenkins-job-builder/>`_.
.. [#] `Ansible Documentation <http://docs.ansible.com//>`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

