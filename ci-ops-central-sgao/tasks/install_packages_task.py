import taskrunner


class InstallPkgs(taskrunner.Task):
    """Install yum and pip packages

    Each set of packages for yum and/or pip will be installed to
    all SSH accessible nodes (i.e. with a floating IP).

        install_pkgs = {
            'task': InstallPkgs,
            'yum_pkgs': 'python-nose',
            'pip_pkgs': 'jenkins-job-builder',
        }
    """
    def __init__(self, yum_pkgs=None, pip_pkgs=None, **kwargs):
        super(InstallPkgs, self).__init__(**kwargs)
        self.yum_pkgs = yum_pkgs
        self.pip_pkgs = pip_pkgs
        self.kwargs = kwargs

    def run(self, context):
        nodes = context['nodes'].nodes

        for node in nodes:
            if self.yum_pkgs is not None:
                node.cmd('yum install -y %s' % self.yum_pkgs)
            if self.pip_pkgs is not None:
                node.cmd('pip install %s' % self.pip_pkgs)

    def cleanup(self, job):
        pass
