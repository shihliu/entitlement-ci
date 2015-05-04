import logging
import json
import os
from time import sleep

import taskrunner

import bkrfactory

LOG = logging.getLogger(__name__)

BEAKER_CONF = \
    (os.environ.get('BEAKER_CONF', '/etc/beaker/client.conf'))

WAIT_TIME = 60
MAX_ATTEMPTS = 60  # Ends up being 60 Minutes
MAX_QUEUED_ATTEMPTS = 4  # If we are in a queued state try this many times


class GetBkrNodes(taskrunner.Task):
    """ Create nodes in Beaker.

    Connects to Beaker and creates a job with an install and reserve task
    """

    def __init__(self, job_group, recipesets, whiteboard,
                 count=1, debug=False, dryrun=False, prettyxml=True,
                 retention_tag='Scratch', random=False,
                 skip_max_attempts=False, skip_no_system=False,
                 metadata=None,
                 resources_file=None, **kwargs):
        """
        :param job_group: job_group in Beaker
        :param recipesets: recipesets allow groupings of values
        :param whiteboard: Message to post as part of the provision
        :param random: Randomly select where beaker resources are pulled from
        :param retention_tag: Retention tag of the job
        :param count: How many nodes to create
        :param debug: Show debug info
        :param dryrun: Create XML don't provision
        :param prettyxml: Pretty way to show xml output
        :param skip_max_attempts: Don't timeout on getting systems
        :param skip_no_system: Accept Warn if device not found
        :param metadata: Extra parameters used to define resources
        :param resources_file: Json file to define resources that are created
        """
        super(GetBkrNodes, self).__init__(**kwargs)
        # auth to the system where we are creating the nodes
        self.count = count
        self.job_group = job_group
        self.debug = debug
        self.dryrun = dryrun
        self.prettyxml = prettyxml
        self.whiteboard = whiteboard
        self.retention_tag = retention_tag
        self.random = random
        self.metadata = metadata
        self.resources_file = resources_file
        self.skip_max_attempts = skip_max_attempts
        self.skip_no_system = skip_no_system
        self.jobs = []
        self.bkr = bkrfactory.BkrFactory()
        self.recipesets = recipesets
        baremetal = 'hypervisor='
        if count > 1 and len(self.recipesets) == 1:
            for idx in range(len(self.recipesets), count):
                self.recipesets.append(self.recipesets[0])
        for idx, recipeset in enumerate(self.recipesets):
            recipeset['hostrequire'].append(baremetal)
        self.max_attempts = MAX_ATTEMPTS * len(self.recipesets)

    def run(self, context):
        """
            Create nodes and wait until they are returned by Beaker
            from installing.
        """
        kwargs = {'debug': self.debug, 'dryrun': self.dryrun,
                  'prettyxml': self.prettyxml,
                  'whiteboard': self.whiteboard, 'job_group': self.job_group,
                  'retention_tag': self.retention_tag, 'random': self.random,
                  'recipesets': self.recipesets}

        self.bkr = bkrfactory.BkrFactory()
        self.jobs = self.bkr.provision(**kwargs)
        self.jobs_url = str(self.jobs)
        self.jobs_url = "https://beaker.engineering.redhat.com/jobs/" \
                        + self.jobs_url[4:-2]
        self.get_bkr_jobs_props()

        LOG.debug("Job results: \n %s", self.job_results)
        idx = 0
        for resource in self.job_results['resources']:
            if 'bkr_data' in self.recipesets[idx]:
                resource.update({'bkr_data': self.recipesets[idx]['bkr_data']})
            if self.metadata is not None:
                resource.update({'metadata': self.metadata})
            idx += 1
        bkr_job_results = open(self.resources_file, 'a')
        json.dump(self.job_results, bkr_job_results, indent=4)

        context['bkr_nodes'] = self.job_results

    def cleanup(self, context):
        """
            Return systems to beaker
        """
        msg = "Teardown of CI Provisioner Beaker resources"
        if os.environ.get('BKR_JOBID') is not None:
            self.bkr.cancel_jobs([os.environ.get('BKR_JOBID')], msg)
            LOG.info("Teardown Beaker Job %s using ENV VAR",
                     os.environ.get('BKR_JOBID'))
        elif context['bkr_nodes']['job_id'] is not None:
            context['bkr_nodes']['job_id'] = 'J:' \
                                             + context['bkr_nodes']['job_id']
            self.bkr.cancel_jobs([context['bkr_nodes']['job_id']], msg)
            LOG.info("Teardown Beaker Job %s",
                     context['bkr_nodes']['job_id'])
        else:
            LOG.info("Beaker Job ID not defined no Teardown")

    def get_bkr_jobs_props(self):
        """
            Check the current status of a beaker job
        """
        attempts = 1
        result = 'New'
        status = 'Running'
        queue_counter = 0
        msg = ''
        while status != 'Aborted' and status != 'Cancelled':
            try:
                LOG.info("Checking Status of job %s", self.jobs_url)
                sleep(WAIT_TIME)
                if self.skip_no_system is True:
                        LOG.info("skip_no_system is True")
                if self.skip_max_attempts is True:
                    LOG.info("skip_max_attempts is True")
                    LOG.info("Attempt %s", attempts)
                    LOG.info("Running for %s Minutes", attempts)
                else:
                    LOG.info("Attempt %s of %s", attempts, self.max_attempts)
                    LOG.info("Running for %s Minutes of %s Minutes", attempts,
                             self.max_attempts)
                self.job_results = self.bkr.check_jobs(self.jobs)
                results = self.job_results['results']
                all_count = len(self.job_results['resources'])
                pass_count = 0
                abort_count = 0
                for resource in self.job_results['resources']:
                    result = resource['result']
                    status = resource['status']
                    if result == 'Pass' or status == "Completed":
                        pass_count += 1
                    elif self.skip_no_system is True and result == 'Warn':
                        pass_count += 1
                    else:
                        pass_count = 0
                    if self.skip_max_attempts is True:
                        LOG.info("skip_max_attempts is True")
                    elif status == 'Queued' \
                            and self.max_attempts - attempts <= 10 \
                            and queue_counter < MAX_QUEUED_ATTEMPTS:
                        attempts -= attempts - 30
                        queue_counter += 1
                    elif queue_counter >= MAX_QUEUED_ATTEMPTS:
                        LOG.error("Giving up on Job %s after %s attempts "
                                  "and %s queued retries, "
                                  "resources stuck in the queued state",
                                  str(self.jobs), attempts, queue_counter)
                        msg = "Resources stuck in the queued state " \
                              "so cancelling Beaker Job"
                        self.bkr.cancel_jobs(self.jobs, msg)
                        raise Exception(msg)
                    if status == 'Aborted':
                        status = 'Aborted'
                        abort_count += 1
                    else:
                        abort_count = 0
                    if result == 'Fail':
                        result = 'Fail'
                    LOG.info("Recipesets status = %s and result = %s",
                             status, result)
                LOG.info("Current job %s result = %s", self.jobs, results)
                if pass_count == all_count:
                    LOG.info("Job was successful status = "
                             "%s and result = %s", status, result)
                    break
                if attempts >= self.max_attempts and self.skip_max_attempts \
                        is False:
                    LOG.error("Giving up on Job %s after %s attempts "
                              "and results = New still",
                              str(self.jobs), attempts)
                    msg = "results = New after %s so cancelling Beaker Job" \
                          % self.max_attempts
                    self.bkr.cancel_jobs(self.jobs, msg)
                    raise Exception(msg)
                if status == 'Cancelled':
                    msg = "Beaker job %s cancelled" % self.jobs
                    LOG.error(msg)
                    self.bkr.cancel_jobs(self.jobs, msg)
                    raise Exception(msg)
                if abort_count == all_count:
                    msg = "All resources aborted for job %s" % self.jobs
                    LOG.error(msg)
                    self.bkr.cancel_jobs(self.jobs, msg)
                    raise Exception(msg)
            except:
                LOG.error("Error getting Job result for job %s",
                          str(self.jobs))
                if attempts >= 30:
                    LOG.error("Giving up on Job %s after %s attempts",
                              str(self.jobs), attempts)
                    msg = "Error in getting Beaker Job Cancelling"
                    self.bkr.cancel_jobs(self.jobs, msg)
                    raise Exception(msg)
            attempts += 1