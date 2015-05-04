import os

from tasks.setup_jslave_task import SetupJslave, TeardownJslave
from targets import provision
from targets import repos

JSLAVE_DEPS = os.environ.get('JSLAVE_DEPS', [])
JENKINS_MASTER_URL = os.environ.get('JENKINS_MASTER_URL',
                                    os.environ.get('JENKINS_URL'))
JENKINS_MASTER_USERNAME = os.environ.get('JENKINS_MASTER_USERNAME')
JENKINS_MASTER_PASSWORD = os.environ.get('JENKINS_MASTER_PASSWORD')

JSLAVELABEL = os.environ.get('JSLAVELABEL', 'ci-ops-jslave')
JSWARM_URL = os.environ.get('JSWARM_URL',
                            'http://repo.jenkins-ci.org/releases/org/'
                            'jenkins-ci/plugins/swarm-client')
JSWARM_VER = os.environ.get('JSWARM_VER', '1.22')
JSWARM_EXECS = os.environ.get('JSWARM_EXECS', '10')
JSWARM_HOME = os.environ.get('JSWARM_HOME', '/home/jenkins')
JSWARM_JAR_LOC = os.environ.get('JSWARM_JAR_LOC', '/root')
SSH_KEYFILE = os.environ.get('SSH_KEYFILE')
JSLAVE_PROCS = os.environ.get('JSLAVE_PROCS', ['swarm'])
SKIP_CUST = os.environ.get('SKIP_CUST', False)
SKIP_CUST = SKIP_CUST in ['true', 'True', True]
SKIP_ANS = os.environ.get('SKIP_ANS', False)
SKIP_ANS = SKIP_ANS in ['true', 'True', True]

if SKIP_ANS is False:
    JSLAVE_DEPS.append('ansible')

setup_jslave = {
    'task': SetupJslave,
    'jslave_deps': JSLAVE_DEPS,
    'jenkins_master_url': JENKINS_MASTER_URL,
    'jenkins_master_username': JENKINS_MASTER_USERNAME,
    'jenkins_master_password': JENKINS_MASTER_PASSWORD,
    'jslave_name': provision.LABEL,
    'jslave_label': JSLAVELABEL,
    'jswarm_url': JSWARM_URL,
    'jswarm_ver': JSWARM_VER,
    'jswarm_execs': JSWARM_EXECS,
    'jswarm_home': JSWARM_HOME,
    'jswarm_jar_loc': JSWARM_JAR_LOC,
    'ssh_keyfile': SSH_KEYFILE,
    'jslave_procs': JSLAVE_PROCS,
    'skip_cust': SKIP_CUST
}

if 'rhel-6' in provision.IMAGE.lower():
    create_jslave = [
        repos.epel,
        repos.epel_testing,
        repos.rhel6_optional,
        repos.rhel6_extras,
        repos.rhos4_puddle,
    ]
    if SKIP_CUST is False:
            create_jslave.append(repos.bkr)
            create_jslave.append(repos.rhel6_consvr)
    create_jslave.append(setup_jslave)
elif 'rhel-7' in provision.IMAGE.lower():
    create_jslave = [
        repos.epel7,
        repos.rhel7_optional,
        repos.rhel7_extras
    ]
    if SKIP_CUST is False:
            create_jslave.append(repos.bkr)
            create_jslave.append(repos.rhel7_consvr)
    create_jslave.append(setup_jslave)
elif 'fed' in provision.IMAGE.lower():
    create_jslave = []
    if SKIP_CUST is False:
            create_jslave.append(repos.bkr_fed)
            create_jslave.append(repos.fedora_consvr)
    create_jslave.append(setup_jslave)
else:
    create_jslave = []
    if SKIP_CUST is False:
        create_jslave.append(repos.bkr)
    create_jslave.append(setup_jslave)

teardown_jslave = {
    'task': TeardownJslave,
    'jslave_procs': JSLAVE_PROCS,
}
