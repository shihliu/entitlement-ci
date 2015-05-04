import logging
import taskrunner
from job_runner.utilities import machine


LOG = logging.getLogger(__name__)

# shortcut for executing a command on all nodes
FOR_ALL_NODES = ('IPS="ALL_NODES";'
                 'IPS="${IPS//,/ }";'
                 'for IP in $IPS; do ssh $IP \'%s\'; done')


class RunCommand(taskrunner.Task):
    """Can be used to execute arbitrary commands.

    This let's you execute command on main node (and from there on others),
    with failure optionaly ignored. Command can be executed in 'run', 'cleanup'
    or both phases.

    Specify command to be executed on main node in way like this:
        clean_var_logs = {
            'task': RunCommand,
            'command': 'rm -rf /var/log/*',
            'when': 'cleanup',
            'ignore_failure': True
        }

    Or on all nodes like:
        update_system = {
            'task': RunCommand,
            'command': 'IPS="ALL_NODES"; IPS="${IPS//,/ }"; for IP in $IPS; do
                ssh $IP "yum upgrade -y";
                done',
        }

    To execute command localy add the `remote=False` option:
        flake8 = {
            'task': RunCommand,
            'command': 'flake8 -v .',
            'remote': False,
        }
    """
    def __init__(self, command, timeout=600, when='run', ignore_failure=False,
                 remote=True, **kwargs):
        """
        :param command: what command to execute, common NODE1/2/...ALL_NODES
            interpolation works
        :param timeout: command timeout in seconds
        :param when: one of ['run', 'cleanup', 'both'], specifies when the
            command should be executed
        :param ignore_failure: ignore errors in the command if True
        :param remote: if False, execute on localhost, if True, execute on the
            nodes
        """
        super(RunCommand, self).__init__(**kwargs)
        self.command = command
        self.timeout = timeout
        self.when = when
        self.ignore_failure = ignore_failure
        self.remote = remote

    def run(self, context):
        self._exec_cmd(context, 'run')

    def cleanup(self, context):
        self._exec_cmd(context, 'cleanup')

    def _exec_cmd(self, context, phase):
        if self.when != 'both' and self.when != phase:
            return

        if self.remote:
            main_node = context['nodes'].main_node
        else:
            main_node = machine.LinuxMachine(
                host='localhost',
                user='nobody',
                password='nopass',
                local=True)

        if 'nodes' in context:
            self.command = context['nodes'].replace_node_vars(self.command)

        try:
            main_node.cmd(self.command,
                          timeout=self.timeout,
                          log_per_line=self.remote)
            # log per line is not implemented for non-remote cmd execution
        except machine.CommandExecutionError as ex:
            if self.ignore_failure:
                LOG.info('Ignoring %s because ignore_failure was specified.'
                         % ex)
            else:
                raise
