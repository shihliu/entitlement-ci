import sys
import json
import os
import logging

LOG = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CI_MESSAGE_JSON_FILE = os.environ.get('CI_MESSAGE_JSON', THIS_DIR
                                      + '/../../ci_message_env.json')

CI_MESSAGE_TXT_FILE = os.environ.get('CI_MESSAGE_TXT', THIS_DIR
                                     + '/../../CI_MESSAGE_ENV.txt')

CI_MESSAGE = os.environ.get('CI_MESSAGE')

if CI_MESSAGE is not None:
    data = json.loads(CI_MESSAGE)
elif sys.argv[1] is not None:
    input_file = open(sys.argv[1], 'r')
    data = json.load(input_file)
    input_file.close()

pretty_data = json.dumps(data, indent=4)
LOG.debug("CI MESSAGE %s" % pretty_data)

brew_taskid = ''
brew_buildid = ''
tag = ''
arches = []
rpms = []
rpm_string = ''
nvr = ''
owner = ''
version = ''
release = ''
pkgname = ''
rpm_pkgs = ''

if 'info' in data:
    brew_taskid = str(data['info']['id'])
    owner = data['info']['owner']
    nvr = '.'.join(str(rpms[0][1]).split('.')[:4])
    pkgname = '-'.join(nvr.split('-')[:-2])
    version = '-'.join(nvr.split('-')[-2:])
    version = '.'.join(version.split('.')[:-1])
    release = '.'.join(nvr.split('.')[-1:])
elif 'build' in data:
    owner = data['build']['owner_name']
    pkgname = data['build']['package_name']
    nvr = data['build']['nvr']
    brew_taskid = str(data['build']['task_id'])
    brew_buildid = str(data['build']['id'])
    tag = data['tag']['name']
    version = data['build']['version']
    release = data['build']['release']

full_msg = {'brew_taskid': brew_taskid, 'brew_buildid': brew_buildid,
            'owner': owner, 'nvr': nvr, 'tag': tag,
            'pkgname': pkgname, 'version': version,
            'release': release, 'arches': arches,
            'rpms': rpm_pkgs}

LOG.info("Generating CI Message JSON file")
CI_MESSAGE_JSON = open(CI_MESSAGE_JSON_FILE, 'w')
json.dump(full_msg, CI_MESSAGE_JSON, indent=4)
CI_MESSAGE_JSON.close()

LOG.info("Generating CI Message Environment Variables File")
f = open(CI_MESSAGE_TXT_FILE, 'w')
f.write("BREW_TASKID=" + brew_taskid + "\n")
f.write("BREW_BUILDID=" + brew_buildid + "\n")
f.write("TAG=" + tag + "\n")
f.write("OWNER=" + str(owner) + "\n")
f.write("NVR=" + nvr + "\n")
f.write("PKGNAME=" + pkgname + "\n")
f.write("VERSION=" + version + "\n")
f.write("RELEASE=" + release + "\n")
f.write("ARCHES=" + ','.join(map(str, arches)) + "\n")
f.write("RPMS=" + rpm_string + "\n")
f.close()
