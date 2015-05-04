import logging
import time
import socket
import os

from ansible.inventory import Inventory
from ansible.playbook import PlayBook
from ansible.runner import Runner
from ansible import callbacks
from ansible import errors
from ansible import utils

LOG = logging.getLogger(__name__)


def ansible_sec_updates(key, hostsfile):

    rc, stdout, stderr = ansible_call_local('Update private key permissions',
                                            'command', 'chmod 600 ' + key,
                                            'localhost', 'root', 10, hostsfile)
    if rc is 0:
        LOG.info("Key permissions updated to 600 and "
                 "set ANSIBLE_HOST_KEY_CHECKING to False")
        os.environ["ANSIBLE_HOST_KEY_CHECKING"] = 'False'
    else:
        msg = "Key permissions FAILED %s, %s, %s" % (rc, stdout, stderr)
        LOG.error(msg)
        raise Exception(msg)


def ansible_call_local(action_info, module, args,
                       pattern='localhost', remote_user='root',
                       forks=10, inventory_file=None, sudo=False,
                       environment=None):
    fatal_err = 0
    inventory = None

    if inventory_file is not None:
        inventory = Inventory(inventory_file)

    runner = Runner(
        module_name=module,
        module_args=args,
        pattern=pattern,
        remote_user=remote_user,
        inventory=inventory,
        forks=forks,
        sudo=sudo,
        environment=environment,
        transport='local',
        timeout=180
    )

    LOG.debug("ansible_call - environment = %s" % environment)

    ret_stdout = ''
    ret_stderr = ''

    results = runner.run()

    for (hostname, result) in results['dark'].items():
        LOG.error("ansible_call: Hostname: %s - %s: Failed. "
                  "Connection error - %s"
                  % (hostname, action_info, result['msg']))
        fatal_err = 1

    LOG.debug("ansible_call - raw results: %s\n" % results)

    for (hostname, result) in results['contacted'].items():
        if result['rc']:
            if 'msg' in result:
                LOG.error("ansible_call - Hostname: %s - %s: Failed.  "
                          "rc = %s  msg = %s\n" % (hostname,
                                                   action_info,
                                                   result['rc'],
                                                   result['msg']))
            elif 'stderr' in result:
                ret_stderr = result['stderr']
                LOG.error("ansible_call - Hostname: %s - %s: Failed.  "
                          "rc = %s  stderr = %s\n"
                          % (hostname,
                             action_info,
                             result['rc'],
                             result['stderr']))
            else:
                ret_stdout = result['stdout']
                LOG.error("ansible_call - Hostname: %s - %s: Failed.  "
                          "stdout = \n%s" % (hostname, action_info,
                                             result['stdout']))
            fatal_err = 1
        else:
            LOG.info("\tansible_call - Hostname: %s - %s: Passed.  "
                     "rc = %s" % (hostname, action_info, result['rc']))
            ret_stdout = result['stdout']
            ret_stderr = result['stderr']

    return fatal_err, ret_stdout, ret_stderr


def ansible_call(action_info, module, args, private_key_file,
                 pattern='testsystems', remote_user='root', forks=10,
                 inventory_file=None, sudo=False, environment=None,
                 background=0, poll=5, retries=0, rc_only=False):

    """Ansible API call wrapper.

    Function to execute an ansible module on specified systems and process
    results.

    Args:
        action_info (str): Short action description of whats being performed.
            This description is used in logging messages.
        module (str): Name of Ansible module to execute.
        args (str): Arguments required by the Ansible module to run.
        private_key_file (str): ssh key that will be used to talk to the
                                systems
        pattern (str, optional): Defaults to 'testsystems'. Grouping
            of systems or system to run ansible module on.
        remote_user (str, optional): Defaults to 'root'.  User that
            will run the commands.
        forks (int, optional): Defaults to 10. Number of concurrent executors.
        inventory_file (str, optional): Defaults to None.
        Ansible host filename.
        sudo (bool, optional): Defaults to False. Run under sudo.
        env (dict, optional): Defaults to None. Dictionary containing env names
            and their values. env['<name>'] = '<value>'
        background (int, optional): Defaults to 0. Greater than 0 causes to run
            in background. Positive value is a timout in seconds. If command
            has not returned in by that time it will be killed.
        poll (int, optional): Defaults to 10. When running in background will
            poll for results every this number of seconds.
        retries (int, optional): Defaults to 0. Number of retries to perform
                                 if failed.
                                 Only retries on failed systems
        rc_only (bool, optional): Defaults to False. If True will only check
                                  return
            code for errors. Else if False will check result for 'failed',
            stdout for 'result: FAIL'
            and rc

    Returns:
    Args:
        results (dict): { 'failures': int, 'success_results': [],
        'failure_results': [] }

    Notes:
        results:
           failures (int): 0 success, non zero number of failures.
           success_results (dict[]): List of Success results
           failure_results (dict[]): List of Failure results

        success_results:
        failure_results: { 'hostname': "", 'status': "", 'rc': int,
                           'stderr': "", 'stdout': "", 'msg': "", 'raw': "" }
           hostname (str): String or IP of target system
           status (str): String Indication of System/Task status
           rc (int): Return code of ansible call execution.
           stderr (str): Contents of ansible call executions stderr
           stdout (str): Contents of ansible call executions stdout
           msg (str): Any message returned by ansible call execution
           raw (): Raw results
    """

    success_list = []
    fail_list = []
    fatal_err = 0
    retries = 1 + retries

    for i in range(1, retries + 1):
        inventory = None
        msg = ""
        raw = ""
        fatal_err = 0
        rc = 0
        stderr = ""
        stdout = ""
        fail_list = []

        if inventory_file is not None:
            inventory = Inventory(inventory_file)

        runner = Runner(
            module_name=module,
            module_args=args,
            private_key_file=private_key_file,
            pattern=pattern,
            remote_user=remote_user,
            forks=forks,
            sudo=sudo,
            inventory=inventory,
            environment=environment,
            timeout=180,
            background=background
        )

        LOG.debug("ansible_call - environment = %s" % environment)

        results = runner.run()

        # Process dark systems (Unable to contact) results
        for (hostname, result) in results['dark'].items():
            LOG.error("ansible_call: Attempt %s: "
                      "Hostname: %s - %s: Failed."
                      "Connection error - %s" % (i, hostname, action_info,
                                                 result['msg']))
            fatal_err += 1
            fail_list.append({'hostname': hostname, 'status': 'DISCONNECTED',
                              'rc': rc, 'stderr': stderr, 'stdout': stdout,
                              'msg': msg, 'raw': result})

        if i < retries + 1:
            time.sleep(poll)

        LOG.debug("ansible_call - Attempt %s: raw results: %s\n"
                  % (i, results))

        if background > 0:
            # Process connected systems results
            results = check_async_results(results, inventory_file,
                                          poll, background)

            fatal_err = fatal_err + results['failures']
            success_list.extend(results['success_results'])
            fail_list.extend(results['failure_results'])

        else:
            # Process connected systems results
            for (hostname, result) in results['contacted'].items():
                rc = 0
                raw = ""
                msg = ""
                stderr = ""
                stdout = ""

                if module == 'async_status':
                    if 'changed' in result:
                        if 'started' not in result \
                                and (result['changed'] is True
                                     or ('finished' in result
                                         and result['finished'] == 1)):
                            raw = result
                            if 'rc' in result:
                                rc = result['rc']
                            if 'stderr' in result:
                                stderr = result['stderr']
                            if 'stdout' in result:
                                stdout = result['stdout']
                            if 'msg' in result:
                                msg = result['msg']

                            # Check for failures
                            if rc_only and rc != 0:
                                fatal_err += 1
                                fail_list.append({'hostname': hostname,
                                                  'status': 'CONNECTED',
                                                  'rc': rc, 'stderr': stderr,
                                                  'stdout': stdout,
                                                  'msg': msg, 'raw': raw})
                                LOG.error("ansible_call: Attempt %s: "
                                          "Hostname: %s - %s: Failed"
                                          % (i, hostname, action_info))
                            elif rc_only is False \
                                    and (rc or 'failed' in result
                                         or 'result: FAIL' in stdout):
                                fatal_err += 1
                                fail_list.append({'hostname': hostname,
                                                  'status': 'CONNECTED',
                                                  'rc': rc, 'stderr': stderr,
                                                  'stdout': stdout,
                                                  'msg': msg, 'raw': raw})
                                LOG.error("ansible_call: Attempt %s: "
                                          "Hostname: %s - %s: Failed"
                                          % (i, hostname, action_info))
                            else:
                                success_list.append({'hostname': hostname,
                                                     'status': 'CONNECTED',
                                                     'rc': rc,
                                                     'stderr': stderr,
                                                     'stdout': stdout,
                                                     'msg': msg, 'raw': raw})

                        else:
                            success_list.append({'hostname': hostname,
                                                 'status': 'RUNNING',
                                                 'rc': rc, 'stderr': stderr,
                                                 'stdout': stdout,
                                                 'msg': msg, 'raw': result})
                    else:
                        fatal_err += 1
                        fail_list.append({'hostname': hostname,
                                          'status': 'CONNECTED',
                                          'rc': rc, 'stderr': stderr,
                                          'stdout': stdout,
                                          'msg': msg, 'raw': raw})
                        LOG.error("ansible_call: Attempt %s: Hostname: %s - "
                                  "%s: Failed" % (i, hostname, action_info))
                else:
                    if 'rc' in result:
                        rc = result['rc']

                    if 'stderr' in result:
                        stderr = result['stderr']

                    if 'stdout' in result:
                        stdout = result['stdout']

                    if 'msg' in result:
                        msg = result['msg']

                    raw = result

                    # Check for failures
                    if rc_only and rc != 0:
                        fatal_err += 1
                        fail_list.append({'hostname': hostname, 'status':
                                          'CONNECTED', 'rc': rc,
                                          'stderr': stderr, 'stdout': stdout,
                                          'msg': msg, 'raw': raw})
                    elif rc_only is False \
                            and (rc or 'failed' in result
                                 or 'result: FAIL' in stdout):
                        fatal_err += 1
                        fail_list.append({'hostname': hostname, 'status':
                                          'CONNECTED', 'rc': rc,
                                          'stderr': stderr,
                                          'stdout': stdout, 'msg': msg,
                                          'raw': raw})
                        LOG.error("ansible_call: Attempt %s: Hostname: %s "
                                  "- %s: Failed" % (i, hostname, action_info))
                    else:
                        success_list.append({'hostname': hostname, 'status':
                                             'CONNECTED', 'rc': rc,
                                             'stderr': stderr,
                                             'stdout': stdout,
                                             'msg': msg, 'raw': raw})

        if fatal_err > 0:
            pattern_list = [d['hostname']
                            for d in fail_list if 'hostname' in d]
            pattern = ""
            pattern = ':'.join([str(i) for i in pattern_list])
            if i < retries + 1:
                time.sleep(poll)
        else:
            break

    return {'failures': fatal_err, 'success_results': success_list,
            'failure_results': fail_list}


def check_async_results(call_results, inventory_file, poll, background):
    """Check results of ansible command performed in background

    Args:
        call_results (dict): ansible call results
        inventory_file (str): Name of ansible hostfile.
        poll (int): Number of seconds to poll for results
        background (int): Number of seconds to run in backgroun (timeout)
            When expired command is killed.

    Returns:
        results (dict): {'timeout': int, 'slept': int,
                         'failures': int, 'success_results': [],
                         'failure_results': [] }

    Notes: Example Dict's
        results:
           failures (int): 0 success, non zero number of failures.
           success_results (dict[]): List of Success results
           failure_results (dict{}): List of Failure results

        success_results:
        failure_results: { 'hostname': "", 'status': "", 'rc': int,
                           'stderr': "", 'stdout': "", 'msg': "" }
           hostname (str): String or IP of target system
           status (str): String Indication of System/Task status
           rc (int): Return code of ansible call execution.
           stderr (str): Contents of ansible call executions stderr
           stdout (str): Contents of ansible call executions stdout
           msg (str): Any message returned by ansible call execution
    """
    tslept = 0
    fatal_err = 0
    fail_list = []
    success_list = []

    while True:
        break_flag = 1
        ajid = ""
        for (hostname, result) in call_results['contacted'].items():
            LOG.info("check_async_results - results = %s "
                     % call_results['contacted'])

            ajid = result['ansible_job_id']

            results = ansible_call("Checking", 'async_status', 'jid=%s' % ajid,
                                   hostname, inventory_file=inventory_file,
                                   background=0)

            # Set fatal_err
            fatal_err = fatal_err + results['failures']

            # Process failure results list
            fail_list.extend(results['failure_results'])

            if results['failures'] > 0:
                call_results['contacted'].pop(hostname, None)
                ansible_call("Cleanup", 'async_status', 'mode=cleanup jid=%s'
                             % ajid, hostname, inventory_file=inventory_file,
                             background=0)

            # Process successful results list
            for result in results['success_results']:
                if result['status'] == 'RUNNING':
                    break_flag = 0

                else:
                    # result['status'] == 'COMPLETED' update to CONNECTED
                    result['status'] = 'CONNECTED'
                    success_list.append(result)
                    call_results['contacted'].pop(hostname, None)
                    ansible_call("Cleanup", 'async_status',
                                 'mode=cleanup jid=%s' % ajid,
                                 hostname, inventory_file=inventory_file,
                                 background=0)

                # Process timed out command
                if tslept > background:
                    result['msg'] = \
                        'FAILED: Command exceeded timeout and was killed'
                    result['status'] = 'CONNECTED'
                    fatal_err += 1
                    fail_list.append(result)
                    break_flag = 1
                    ansible_call("Cleanup", 'async_status',
                                 'mode=cleanup jid=%s' % ajid,
                                 hostname, inventory_file=inventory_file,
                                 background=0)

        if break_flag:
            break

        # Poll
        time.sleep(poll)
        tslept = tslept + poll
        tleft = background - tslept
        if tleft >= 0:
            LOG.info("ansible_call - Timeout = %s - Time remaining = %s"
                     % (background, tleft))
        else:
            LOG.info("ansible_call - Timeout Expires - "
                     "Please wait process being terminated. "
                     "Will continue shortly")

    return {'failures': fatal_err, 'success_results': success_list,
            'failure_results': fail_list}


def fqdn_ip(hostname):
    addr = socket.gethostbyname(hostname)
    return addr


def ansible_playbook_call(name, playbook, private_key_file,
                          inventory_file=None, remote_user='root',
                          extra_vars=None):
    """Ansible Playbook API call wrapper.

    Function to execute a ansible playbook.

    Args:
        name (str): Short description of playbook being run.
            This description is used in logging messages.
        playbook (str): Name of playbook file to execute including path.
        private_key_file (str): ssh key that will be used to talk to the
                                systems
        inventory_file (str, optional): Defaults to None. Ansible host filename
        remote_user (str, optional): Defaults to 'root'.  User that
            will run the commands.
        extra_vars (dict, optional): Defaults to None. Values need by playbook.
            extra_vars['<name>'] = '<value>'

    Returns:
        results (dict): { 'failures': int, 'success_results': [],
                          'failure_results': [] }

    Notes:
        results:
           failures (int): 0 success, non zero number of failures.
           success_results ([]): List of Successful hosts
           failure_results ([]): List of Failure hosts
    """

    fatal_err = 0
    fail_list = []
    success_list = []
    inventory = None

    if inventory_file is not None:
        inventory = Inventory(inventory_file)

    if not os.path.exists(playbook):
        raise errors.AnsibleError("the playbook: %s could not be found"
                                  % playbook)
    if not (os.path.isfile(playbook)
            or os.stat.S_ISFIFO(os.stat(playbook).st_mode)):
        raise errors.AnsibleError("the playbook: "
                                  "%s does not appear to be a file" % playbook)

    # run all playbooks specified on the command line
    # let inventory know which playbooks are using so it can know the basedirs
    inventory.set_playbook_basedir(os.path.dirname(playbook))

    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats,
                                                  verbose=utils.VERBOSITY)

    pb = PlayBook(playbook=playbook, inventory=inventory, stats=stats,
                  callbacks=playbook_cb, runner_callbacks=runner_cb,
                  extra_vars=extra_vars)
    pb.remote_user = remote_user
    pb.private_key_file = private_key_file
    results = pb.run()

    LOG.debug("ansible_playbook_call - raw results: %s\n" % results)

    for (hostname, result) in results.items():
        if result['unreachable'] > 0:
            LOG.error("ansible_playbook_call: Hostname: %s - %s: Failed. "
                      "Connection error" % (hostname, name))
            fail_list.append(hostname)
            fatal_err += 1
        elif result['failures'] > 0:
            LOG.error("ansible_playbook_call: Hostname: %s - %s: Failed. "
                      "Tasks failed" % (hostname, name))
            fail_list.append(hostname)
            fatal_err += 1
        elif result['ok'] + result['skipped'] > 0:
            LOG.info("\tansible_playbook_call - Hostname: %s - %s: Passed."
                     % (hostname, name))
            success_list.append(hostname)
        else:
            LOG.error("ansible_playbook_call: Hostname: %s - %s: Failed. "
                      "Unexpected error" % (hostname, name))
            fail_list.append(hostname)
            fatal_err += 1

    return {'failures': fatal_err, 'success_results': success_list,
            'failure_results': fail_list}


def log_ansible_call(results):
    """Log Ansible call results.

    Function to format and log results obtained from ansible call.

    Args:
        results (dict): { 'failures': int, 'success_results': [],
                          'failure_results': [] }

    Notes:
        results:
           failures (int): 0 success, non zero number of failures.
           success_results (dict[]): List of Success results
           failure_results (dict{}): List of Failure results

        success_results:
        failure_results: { 'hostname': "", 'status': "", 'rc': int, 'stderr':
                           "", 'stdout': "", 'msg': "" }
           hostname (str): String or IP of target system
           status (str): String Indication of System/Task status
           rc (int): Return code of ansible call execution.
           stderr (str): Contents of ansible call executions stderr
           stdout (str): Contents of ansible call executions stdout
           msg (str): Any message returned by ansible call execution
           raw (): Raw results
    """
    LOG.info("ANSIBLE CALL RESULTS")
    LOG.info("SUCCESSES %s" % len(results['success_results']))
    if len(results['success_results']) > 0:
        for result in results['success_results']:
            if 'msg' in result:
                if result["msg"] == "":
                    result["msg"] = None

            if 'hostname' in result and 'status' in result:
                LOG.info("\thostname: %s\tstatus: %s" % (result['hostname'],
                                                         result['status']))
            if 'rc' in result or 'stdout' in result or 'stderr' in result:
                LOG.info("\tansible_call output\n\trc = %s\n\tmsg = %s\n\t"
                         "stderr Output:\n\t%s\n\tstdout Output:\n\t%s\n"
                         % (result['rc'], result['msg'], result['stderr'],
                            result['stdout']))
            if 'raw' in result:
                LOG.debug("\n\tRaw Result:\n\t%s\n\t"
                          % result['raw'])

    LOG.info("FAILURES %s" % results['failures'])
    if len(results['failure_results']) > 0:
        for result in results['failure_results']:
            if 'msg' in result:
                if result["msg"] == "":
                    result["msg"] = None
            if 'hostname' in result and 'status' in result:
                LOG.info("\thostname: %s\tstatus: %s" % (result['hostname'],
                                                         result['status']))
            if 'rc' in result or 'stdout' in result or 'stderr' in result:
                LOG.info("\tansible_call output\n\trc = %s\n\tmsg = %s\n\t"
                         "stderr Output:\n\t%s\n\tstdout Output:\n\t%s\n"
                         % (result['rc'], result['msg'], result['stderr'],
                            result['stdout']))
            if 'raw' in result:
                LOG.debug("\n\tRaw Result:\n\t%s\n\t"
                          % result['raw'])


def add_ansible_hosts(hostfile, useips, runlocal, slaves,
                      testsystems, pattern='testsystems'):
    """Create ansible hosts file.

    Args:
        hostfile (str): Name of ansible hostfile.
        runlocal (bool): Add ansible_connection=local
        useips (bool): Use system names or ips in hostfile.
            Valid values are True or False
        slaves (dict[]): List of SYS dictionaries describing slave systems.
            See Notes for SYS definition.
        testsystems (dict[]): List of SYS dictionaries describing test systems.
            See Notes for SYS definition.
        pattern (string) run against the test resources that are added

    Notes: Example Dict's
        SYS = {'name': '', 'ip': '', 'distro': {}}
        DISTRO = {'name': '', 'variant': '', 'arch': '', 'ver': '',
                  'os_type': '', 'base_repo_url': '', 'repo_urls': []}

    Returns:
        results (dict): {'failures': int, 'success_results': [],
                         'failure_results': [] }

    Notes: Example Dict's
        results:
           failures (int): 0 success, non zero number of failures.
           success_results (dict[]): List of Success results
           failure_results (dict{}): List of Failure results

        success_results:
        failure_results: { 'hostname': "", 'status': "", 'rc': int,
                           'stderr': "", 'stdout': "", 'msg': "" }
           hostname (str): String or IP of target system
           status (str): String Indication of System/Task status
           rc (int): Return code of ansible call execution.
           stderr (str): Contents of ansible call executions stderr
           stdout (str): Contents of ansible call executions stdout
           msg (str): Any message returned by ansible call execution

    """

    msg = ""
    rc = 0
    stderr = ""
    stdout = ""

    try:
        of = open(hostfile, "w")
        of.write("[local]\n")
        of.write("localhost\tansible_connection=local\n\n")

        if slaves:
            of.write("[slaves]\n")
            for system in slaves:
                if useips is True:
                    of.write("%s" % system['ip'])
                else:
                    of.write("%s" % system['name'])
                if runlocal is True:
                    of.write("\tansible_connection=local\n\n")
                else:
                    of.write("\n\n")

        inventory = {}
        for system in testsystems:
            if 'role' in system and 'product' in system \
                    and 'version' in system:
                key = "%s-%s-%s" % (system['product'].replace(' ', '_'),
                                    system['version'].replace(' ', '_'),
                                    system['role'].replace(' ', '_'))
                if key in inventory:
                    inventory[key].append(system['ip'])
                else:
                    inventory[key] = [system['ip']]

        if inventory:
            # Individual systems
            for group in inventory:
                if len(inventory[group]) > 1:
                    for i, ip in enumerate(inventory[group]):
                        of.write("[%s-%s]\n%s\n\n" % (group, i+1, ip))
                else:
                    of.write("[%s]\n%s\n\n" % (group, inventory[group][0]))

            # Group
            for group in inventory:
                if len(inventory[group]) > 1:
                    of.write("[%s:children]\n" % group)
                    for i, ip in enumerate(inventory[group]):
                        of.write("%s-%s\n" % (group, i+1))
                    of.write("\n")

        else:
            of.write("[" + pattern + "]\n")
            if useips is True:
                for system in testsystems:
                    of.write("%s\n" % system['ip'])
            else:
                for system in testsystems:
                    of.write("%s\n" % system['name'])
        of.close()

    except (OSError, IOError) as e:
        LOG.error("\nadd_ansible_hosts: Issue creating ansible host file - %s"
                  % e)
        raise Exception("Failed to create ansible hosts file!")
        return 1, rc, stderr, stdout, msg
