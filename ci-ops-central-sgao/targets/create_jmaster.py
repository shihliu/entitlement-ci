import os

from tasks.create_jenkins_task import CreateJenkins
from targets import provision
from targets import repos

NEW_JENKINS_NAME = os.environ.get('NEW_JENKINS_NAME',
                                  os.environ.get('USER', 'user'))
SSH_KEYFILE = os.environ.get('SSH_KEYFILE')
SSL_CERT = os.environ.get('SSL_CERT')
SSL_KEY = os.environ.get('SSL_KEY')
KEYSTORE_PASS = os.environ.get('KEYSTORE_PASS', 'changeme')
JENKINS_USER = os.environ.get('JENKINS_USER')
API_TOKEN = os.environ.get('API_TOKEN')
CUSTOM_PLUGINS = os.environ.get('CUSTOM_PLUGINS', '').split(',')
CUSTOM_PACKAGES = os.environ.get('CUSTOM_PACKAGES', '').split(',')
CUSTOM_PYMODS = os.environ.get('CUSTOM_PYMODS', '').split(',')

CFG_JENKINS_VIEWS = False

plugins_base = ['git', 'xunit', 'ansicolor', 'multiple-scms', 'rebuild',
                'ws-cleanup', 'gerrit-trigger', 'parameterized-trigger',
                'envinject', 'email-ext', 'sonar', 'copyartifact',
                'timestamper', 'build-timeout', 'jobConfigHistory',
                'test-stability', 'jenkins-multijob-plugin',
                'dynamicparameter', 'swarm', 'shiningpanda',
                'scm-api', 'ownership', 'mask-passwords', 'role-strategy',
                'thinBackup']
plugins_extra = ['groovy-postbuild', 'gerrit-trigger', 'jobConfigHistory',
                 'buildresult-trigger', 'greenballs', 'jquery', 'jquery-ui',
                 'nodelabelparameter', 'token-macro', 'disk-usage',
                 'tmpcleaner', 'depgraph-view', 'sonargraph-plugin',
                 'throttle-concurrents', 'toolenv',
                 'copy-to-slave', 'scripttrigger', 'flexible-publish',
                 'PrioritySorter', 'python', 'redhat-ci-plugin',
                 'credentials-binding', 'update-sites-manager',
                 'conditional-buildstep', 'postbuildscript', 'ircbot']
plugins_visual = ['ColumnPack-plugin', 'ColumnsPlugin', 'build-node-column',
                  'build-view-column', 'built-on-column', 'compact-columns',
                  'build-pipeline-plugin', 'configure-job-column-plugin',
                  'console-column-plugin', 'console-tail', 'cron_column',
                  'description-column-plugin', 'email-ext-recipients-column',
                  'extra-columns', 'jobtype-column', 'nodenamecolumn',
                  'progress-bar-column-plugin', 'project-stats-plugin',
                  'schedule-build-plugin', 'nested-view', 'sectioned-view']

PLUGINS = os.environ.get('PLUGINS', 'plugins_all')
JOBS_ENABLED = os.environ.get('JOBS_ENABLED', 'True')
HTTPS_ENABLED = os.environ.get('HTTPS_ENABLED', 'False')

if PLUGINS == 'plugins_base':
    PLUGINS = plugins_base + CUSTOM_PLUGINS
elif PLUGINS == 'plugins_extra':
    PLUGINS = plugins_base + plugins_extra + CUSTOM_PLUGINS
elif PLUGINS == 'plugins_visual':
    PLUGINS = plugins_visual + CUSTOM_PLUGINS
    CFG_JENKINS_VIEWS = True
elif PLUGINS == 'plugins_all':
    PLUGINS = plugins_base + plugins_extra + plugins_visual + CUSTOM_PLUGINS
    CFG_JENKINS_VIEWS = True

packages_base = ['jenkins', 'git', 'java-1.6.0-openjdk', 'python-paramiko']
packages_extra = ['graphviz', 'lftp', 'gcc compat-gcc-34.x86_64',
                  'libffi-devel', 'python-devel', 'openssl-devel',
                  'libxml2-devel', 'libxslt-devel', 'krb5-workstation',
                  'python-futures', 'python-six', 'python-unittest2',
                  'python-configobj', 'python-nose', 'ansible']

pip_base = ['jenkins-job-builder==1.1.0', 'taskrunner']
pip_extra = ['argparse', 'python-foreman']
pip_os = ['python-keystoneclient', 'python-glanceclient', 'python-novaclient']

ci_ops_jenkins = {
    'task': CreateJenkins,
    'plugins': PLUGINS,
    'rpm_deps': packages_base + packages_extra + CUSTOM_PACKAGES,
    'pip_deps': pip_base + pip_extra + pip_os + CUSTOM_PYMODS,
    'install_citools': True,
    'citools_repo': 'git://git.app.eng.bos.redhat.com/ci-ops-central.git',
    'jobs_repo': 'git://git.app.eng.bos.redhat.com/ci-ops-projex.git',
    'install_qetasks': False,
    'create_jobs': True,
    'jobs_enabled': JOBS_ENABLED,
    'cfg_results_view': CFG_JENKINS_VIEWS,
    'ssh_keyfile': SSH_KEYFILE,
    'https_enabled': HTTPS_ENABLED,
    'ssl_cert': SSL_CERT,
    'ssl_key': SSL_KEY,
    'keystore_pass': KEYSTORE_PASS,
    'jenkins_user': JENKINS_USER,
    'api_token': API_TOKEN,
    'jenkins_env_vars': {
        'JENKINS_NAME': NEW_JENKINS_NAME,
        'JENKINS_MASTER_URL': '',
        'JOB_BUILDER_USER': '',
        'JOB_BUILDER_PASS': '',
        'SITE': provision.SITE,
    },
}

if 'rhel-6' in provision.IMAGE:
    create_jenkins = [
        repos.jenkins,
        repos.rhel6_optional,
        repos.rhel6_latest,
        repos.rhel6_consvr,
        repos.rhel6_extras,
        repos.epel,
        repos.bkr,
        repos.rhos4_puddle,
        ci_ops_jenkins
    ]
elif 'rhel-7' in provision.IMAGE:
    create_jenkins = [
        repos.jenkins,
        repos.rhel7_optional,
        repos.rhel7_latest,
        repos.rhel7_consvr,
        repos.rhel7_extras,
        repos.epel7,
        repos.bkr,
        repos.rhos4_puddle,
        ci_ops_jenkins
    ]
elif 'fedora' in provision.IMAGE:
    create_jenkins = [
        repos.jenkins,
        repos.bkr_fed,
        ci_ops_jenkins
    ]
else:
    create_jenkins = [
        repos.jenkins,
        repos.bkr,
        repos.rhos4_puddle,
        ci_ops_jenkins
    ]

# RHOS Jenkins requirements, RHOS QE agrees to keep this updated

plugins_rhos = ['jobConfigHistory', 'buildresult-trigger', 'test-stability',
                'dynamicparameter', 'scm-api', 'token-macro', 'swarm',
                'scripttrigger', 'groovy-postbuild', 'shiningpanda',
                'jenkins-multijob-plugin', 'ownership']

packages_rhos = ['lftp']

pip_rhos = ['taskrunner', 'pbr==0.6', 'python-keystoneclient',
            'python-glanceclient', 'python-novaclient']

rhos_jenkins = {
    'task': CreateJenkins,
    'plugins': plugins_base + plugins_rhos,
    'rpm_deps': packages_base + packages_rhos,
    'pip_deps': pip_base + pip_rhos,
    'jobs_repo': 'git://git.app.eng.bos.redhat.com/rhos-qe-jenkins.git',
    'install_qetasks': False,
    'create_jobs': True,
    'jobs_enabled': False,
    'jenkins_env_vars': {
        'JENKINS_NAME': NEW_JENKINS_NAME,
        'JENKINS_MASTER_URL': '',
        'JOB_BUILDER_USER': '',
        'JOB_BUILDER_PASS': '',
        'SITE': provision.SITE,
    },
}

create_rhos_jenkins = [
    repos.jenkins,
    repos.bkr,
    rhos_jenkins]
