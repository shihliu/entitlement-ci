import os

from tasks.manage_jobs_task import ManageJobs
from targets import provision

UPDATE_JOBS = os.environ.get('UPDATE_JOBS', 'False')
JOBS_REPO = os.environ.get('JOBS_REPO',
                           'git://git.app.eng.bos.redhat.com/'
                           'ci-ops-projex.git')
FORCE_UPDATE = os.environ.get('FORCE_UPDATE', 'False')
ENABLE_ALL_JOBS = os.environ.get('ENABLE_ALL_JOBS', 'False')
DISABLE_ALL_JOBS = os.environ.get('DISABLE_ALL_JOBS', 'False')
JENKINS_USER = os.environ.get('JENKINS_USER')
API_TOKEN = os.environ.get('API_TOKEN')

mock_create_nodes = provision.mock_create_nodes

manage_jobs = {
    'task': ManageJobs,
    'jobs_repo': JOBS_REPO,
    'update_jobs': UPDATE_JOBS,
    'force_update': FORCE_UPDATE,
    'enable_all_jobs': ENABLE_ALL_JOBS,
    'disable_all_jobs': DISABLE_ALL_JOBS,
    'jenkins_user': JENKINS_USER,
    'api_token': API_TOKEN,
}
