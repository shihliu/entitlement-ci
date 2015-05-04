import os

from tasks.create_jenkins_task import CreateJenkins
from targets import common
from targets import repos

NEW_JENKINS_NAME = os.environ.get('NEW_JENKINS_NAME',
                                  os.environ.get('USER', 'user'))

_jenkins = {
    'task': CreateJenkins,
    'plugins': ['git', 'xunit', 'ansicolor', 'multiple-scms', 'rebuild',
                'groovy-postbuild', 'ws-cleanup', 'gerrit-trigger',
                'jobConfigHistory', 'parameterized-trigger',
                'envinject', 'email-ext', 'sonar',
                'buildresult-trigger', 'jenkins-testswarm-plugin'],
    'jobs_deps': ['python-paramiko'],
    'jobs_repo': 'git://git.app.eng.bos.redhat.com/ci-ops-projex.git',
    'install_qetasks': True,
    'create_jobs': True,
    'jenkins_env_vars': {
        'JENKINS_NAME': NEW_JENKINS_NAME,
        'JOB_BUILDER_USER': '',
        'JOB_BUILDER_PASS': '',
        'SITE': common.SITE,
    },
}

if common.MIRROR_HOST:
    _jenkins['jobs_repo'] = '%s/ci-ops-projex' % common.MIRROR_HOST

create_jenkins = [
    repos.jenkins,
    _jenkins,
]
