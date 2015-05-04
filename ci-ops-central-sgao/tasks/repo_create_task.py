import taskrunner


REPO_DIR = '/etc/yum.repos.d'


class RepoCreate(taskrunner.Task):
    """Create a custom yum repository on nodes.

    Each parameter given to the class will written into 'name.repo' file, where
    the name is decided by the 'name' param. The file will be distributed to
    all SSH accessible nodes (i.e. with a floating IP).

        repocreate = {
            'task': RepoCreate,
            'name': 'example',
            'foo': 'bar',
            'cat': 'dog'
        }

    The result will be a file 'example.repo' with the content::

        [example]
        foo=bar
        cat=dog
    """
    def __init__(self, name='customrepo', **kwargs):
        super(RepoCreate, self).__init__(name, **kwargs)
        kwargs['name'] = name
        self.kwargs = kwargs

    def run(self, context):
        nodes = context['nodes'].nodes
        filepath = '%s/%s.repo' % (REPO_DIR, self.name)
        data = ['[%s]' % self.name]
        for key, value in self.kwargs.items():
            data.append('%s=%s' % (key, value))
        for node in nodes:
            node.cmd('echo \'%s\' > %s' % ('\n'.join(data), filepath))

    def cleanup(self, job):
        pass
