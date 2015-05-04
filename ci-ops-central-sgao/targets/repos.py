from taskrunner import extend_dict

from tasks.repo_create_task import RepoCreate
from tasks.run_command_task import RunCommand, FOR_ALL_NODES
from targets import common

DOWNLOAD_SITE = 'http://download.lab.bos.redhat.com'
RELENG_URL = DOWNLOAD_SITE + '/rel-eng'

FEDORAPEOPLE = 'http://repos.fedorapeople.org/repos/openstack/'
BOSTON_RDO = 'http://team.virt.bos.redhat.com/openstack/'
BOSTON_RHOS = 'http://download.lab.bos.redhat.com/rel-eng/OpenStack/'


# TEMPLATE
repo_create = {
    'task': RepoCreate,
    'enabled': 1,
    'skip_if_unavailable': 0,
    'gpgcheck': 0,
}


# BASIC REPOS
rhel65base = {
    # contains rhel6.5-z, lb, ha, rs and server
    'task': RunCommand,
    'command': (FOR_ALL_NODES
                % 'curl -o /etc/yum.repos.d/rhel-6.5.repo'
                  ' http://shell.bos.redhat.com/~lhh/rhel-6.5.repo')
}

epel = extend_dict(repo_create, {
    'name': 'epel',
    'mirrorlist': ('https://mirrors.fedoraproject.org/'
                   'metalink?repo=epel-6&arch=$basearch'),
    'failovermethod': 'priority',
})

epel7 = extend_dict(epel, {
    'mirrorlist': ('https://mirrors.fedoraproject.org/'
                   'metalink?repo=epel-7&arch=$basearch')
})

epel_testing = extend_dict(repo_create, {
    'name': 'testing-epel',
    'mirrorlist': ('https://mirrors.fedoraproject.org/'
                   'metalink?repo=testing-epel7&arch=$basearch'),
    'failovermethod': 'priority',
})

if 'rhel-6' in common.DISTRIBUTION:
    epel_testing['mirrorlist'] = ('https://mirrors.fedoraproject.org/'
                                  'metalink?repo=testing-epel6'
                                  '&arch=$basearch')
fedora_testing = {
    'task': RunCommand,
    'command': ("sed -i 's/enabled=0/enabled=1/' "
                "/etc/yum.repos.d/fedora-updates-testing.repo")
}

fedora_rawhide = extend_dict(repo_create, {
    'name': 'rawhide',
    'mirrorlist': ('https://mirrors.fedoraproject.org/'
                   'metalink?repo=rawhide&arch=$basearch')
})

epel7_white = extend_dict(epel7, {
    'includepkgs': 'euca2ools bash-completion python-pip'
})

epel7_rdopkg = extend_dict(epel7, {
    'name': 'epel7-rdopkg',
    'includepkgs': 'python-html5lib python-beautifulsoup4 python-blessings '
                   'python-html5lib'
})

epel_rdopkg = extend_dict(epel, {
    'name': 'epel-rdopkg',
    'includepkgs': 'python-html5lib python-beautifulsoup4 python-blessings '
                   'python-html5lib git-review'
})

# RHEL-6

rhel6_latest = extend_dict(repo_create, {
    'name': 'rhel6-latest',
    'baseurl': (RELENG_URL
                + '/latest-RHEL-6/6/Server/x86_64/os/'),
})

rhel6_optional = extend_dict(repo_create, {
    'name': 'rhel6-optional',
    'baseurl': (RELENG_URL
                + '/latest-RHEL-6/6/Server/optional/x86_64/os/'),
})

rhel6_extras = extend_dict(repo_create, {
    'name': 'rhel6-extras',
    'baseurl': (RELENG_URL
                + '/latest-EXTRAS-6-RHEL-6/compose/Server/x86_64/os/'),
})

# RHEL-7
rhel7_released = extend_dict(repo_create, {
    'name': 'rhel7-released',
    'baseurl': (DOWNLOAD_SITE
                + '/released/RHEL-7/7.0/Server/x86_64/os/'),
})

rhel7_latest = extend_dict(repo_create, {
    'name': 'rhel7-latest',
    'baseurl': (RELENG_URL
                + '/latest-RHEL-7/compose/Server/x86_64/os/'),
})

rhel7_optional = extend_dict(repo_create, {
    'name': 'rhel7-optional',
    'baseurl': (RELENG_URL
                + '/latest-RHEL-7/compose/Server-optional/x86_64/os/'),
})

rhel7_extras = extend_dict(repo_create, {
    'name': 'rhel7-extras',
    'baseurl': (RELENG_URL
                + '/latest-EXTRAS-7-RHEL-7/compose/Server/x86_64/os/'),
})

rhel7_z = extend_dict(repo_create, {
    'name': 'rhel7z',
    'baseurl': (RELENG_URL
                + '/repos/rhel-7.0-z/x86_64/'),
})

rhel7_ha = extend_dict(repo_create, {
    'name': 'rhel7-ha',
    'baseurl': (RELENG_URL
                + '/latest-RHEL-7/compose/Server/x86_64/os/'
                'addons/HighAvailability/'),
})


# atm this is also candidate, though 'official' configured by rhos-release
# https://code.engineering.redhat.com/gerrit/gitweb?p=rhos-release.git;
# a=blob;f=repos/rhos-release-5-rhel-7.repo;hb=HEAD#l18
# and later it could/should became non-candidate
rhel7_mrg = extend_dict(repo_create, {
    'name': 'rhel7-mrg',
    'baseurl': (RELENG_URL
                + '/repos/mrg-2.5-rhel-7-candidate/$basearch/'),
})

rhel7_mrg_candidate = extend_dict(repo_create, {
    'name': 'rhel7-mrg-candidate',
    'baseurl': 'http://mrgrepo.usersys.redhat.com/mrg-2.5-rhel-7-candidate/'
})

rhel7_base = [rhel7_released, rhel7_z, epel7_white]

rdo_rhel_base = [epel, rhel65base, rhel6_optional]
rdo_rhel7_base = [epel7, rhel7_released, rhel7_z, rhel7_optional,
                  rhel7_ha, rhel7_extras]

# JENKINS
jenkins = {
    'task': RunCommand,
    'command': ('curl -o /etc/yum.repos.d/jenkins.repo'
                ' http://pkg.jenkins-ci.org/redhat-stable/jenkins.repo'
                ' && rpm --import'
                ' http://pkg.jenkins-ci.org/redhat-stable/jenkins-ci.org.key')
}

# BEAKER
bkr = {
    'task': RunCommand,
    'command': ('curl -o '
                '/etc/yum.repos.d/beaker-client-RedHatEnterpriseLinux.repo'
                ' https://beaker-project.org/'
                'yum/beaker-client-RedHatEnterpriseLinux.repo'
                ' && yum install -y libxslt-python beaker-client')
}

bkr_fed = {
    'task': RunCommand,
    'command': ('curl -o /etc/yum.repos.d/beaker-client-Fedora.repo'
                ' https://beaker-project.org/yum/beaker-client-Fedora.repo'
                ' && yum install -y libxslt-python beaker-client')
}

# Autobkr
autobkr = {
    'task': RunCommand,
    'command': ('curl -o '
                '/etc/yum.repos.d/autobkr.repo'
                ' http://autobkr.app.eng.bos.redhat.com/'
                'repos/autobkr/autobkr.repo'
                ' && yum install -y autobkr-client')
}

# CONSERVER
rhel6_consvr = {
    'task': RunCommand,
    'command': ('curl -o /etc/yum.repos.d/rhel6-eng-rhel-6.repo'
                ' http://yum.devel.redhat.com/pub/yum/repo_files/'
                'rhel6-eng-rhel-6.repo'
                ' && yum --enablerepo=eng-rhel-6 install -y conserver-client')
}

rhel7_consvr = {
    'task': RunCommand,
    'command': ('curl -o /etc/yum.repos.d/rhel7-eng-rhel-7.repo'
                ' http://yum.devel.redhat.com/pub/yum/repo_files/'
                'rhel7-eng-rhel-7.repo'
                ' && yum --enablerepo=eng-rhel-7 install -y conserver-client')
}

fedora_consvr = {
    'task': RunCommand,
    'command': ('yum install -y conserver-client')
}

# RHOS
# Grizzly
rhos3_puddle = extend_dict(repo_create, {
    'name': 'puddle',
    'baseurl': (BOSTON_RHOS + 'Grizzly/%s/%s$basearch/os/'
                % (common.GRIZZLY_PUDDLE,
                   common.grizzly_subfolder(common.GRIZZLY_PUDDLE)))
})

# Havana
rhos4_puddle = extend_dict(repo_create, {
    'name': 'puddle',
    'baseurl': (BOSTON_RHOS + '4.0/%s/RHOS-4.0/$basearch/os/'
                % common.HAVANA_PUDDLE)
})

rhos4_beta_extra = {
    'task': RunCommand,
    'command': (FOR_ALL_NODES
                % 'curl -o /etc/yum.repos.d/rhos-other.repo'
                  ' http://shell.bos.redhat.com/~lhh/rhos-other.repo')
}

# RDO
# Havana
# production
rdo_havana = extend_dict(repo_create, {
    'name': 'rdo-havana-production',
    'baseurl': FEDORAPEOPLE + 'openstack-havana/epel-6/'
})
rdo_havana_fedora = extend_dict(repo_create, {
    'name': 'rdo-havana-production',
    'baseurl': FEDORAPEOPLE + 'openstack-havana/fedora-19/'
})
# staging
rdo_havana_stage = extend_dict(repo_create, {
    'name': 'rdo-havana-stage',
    'baseurl': BOSTON_RDO + 'openstack-havana/epel-6/'
})
rdo_havana_stage_fedora = extend_dict(repo_create, {
    'name': 'rdo-havana-stage',
    'baseurl': BOSTON_RDO + 'openstack-havana/fedora-19/'
})

# Icehouse
# production
rdo_icehouse = {
    'task': RunCommand,
    'command': (FOR_ALL_NODES
                % ('yum install -y ' + FEDORAPEOPLE + "openstack-icehouse"
                   "/rdo-release-icehouse.rpm"))
}

# poodles (production snapshots)
rdo_havana_poodle = extend_dict(repo_create, {
    'name': 'rdo-icehouse-poodle',
    'baseurl': 'http://rhev-i8c-02.mpc.lab.eng.bos.redhat.com/'
               'openstack-ci-repo-snapshots/pending/repos/havana-epel-6/'
})
rdo_icehouse_poodle = extend_dict(repo_create, {
    'name': 'rdo-icehouse-stage',
    'baseurl': 'http://rhev-i8c-02.mpc.lab.eng.bos.redhat.com/'
               'openstack-ci-repo-snapshots/pending/repos/icehouse-epel-6/'
})

print_poodle_mark = {
    'task': RunCommand,
    'command': ('echo -n "Build mark: puddle=" && curl '
                'http://rhev-i8c-02.mpc.lab.eng.bos.redhat.com/'
                'openstack-ci-repo-snapshots/pending/repos/timestamp'),
    'remote': False,
}

# staging
rdo_icehouse_stage = extend_dict(repo_create, {
    'name': 'rdo-icehouse-stage',
    'baseurl': BOSTON_RDO + 'openstack-icehouse/epel-6/'
})
rdo_icehouse_stage_fedora = extend_dict(repo_create, {
    'name': 'rdo-icehouse-stage',
    'baseurl': BOSTON_RDO + 'openstack-icehouse/fedora-20/'
})


_rdopkg_base = 'http://jruzicka01.lab.eng.brq.redhat.com/repos/rdopkg/'
rdopkg_rhel = extend_dict(repo_create, {
    'name': 'rdopkg',
    'baseurl': (_rdopkg_base + 'rhel/$releasever/'),
})
rdopkg_fedora = extend_dict(rdopkg_rhel, {
    'baseurl': (_rdopkg_base + 'fedora/'),
})

combinations = {}

if 'rhel-6' in common.DISTRIBUTION:
    combinations.update({
        'rhos-3.0': [rhos3_puddle],
        'rhos-4.0': [rhos4_beta_extra, rhos4_puddle],
        'rdo-grizzly': [epel],
    })
    if 'rhel-6.4' in common.DISTRIBUTION:
        combinations.update({'rhos-3.0': [rhos3_puddle]})
    elif 'rhel-6.5' in common.DISTRIBUTION:
        combinations.update({
            'rhos-3.0': [rhel65base, rhos3_puddle],
            'rhos-4.0': [rhel65base, rhos4_beta_extra, rhos4_puddle],
            'rdo-havana': rdo_rhel_base + [rdo_havana],
            'rdo-havana_stage': rdo_rhel_base + [rdo_havana_stage],
            'rdo-havana_poodle': rdo_rhel_base + [rdo_havana_poodle,
                                                  print_poodle_mark],
            'rdo-icehouse': rdo_rhel_base + [rdo_icehouse],
            'rdo-icehouse_stage': rdo_rhel_base + [rdo_icehouse_stage],
            'rdo-icehouse_poodle': rdo_rhel_base + [rdo_icehouse_poodle,
                                                    print_poodle_mark],
            'upstream-master': rdo_rhel_base + [rdo_icehouse],
            'upstream-icehouse': rdo_rhel_base + [rdo_icehouse],
            'upstream-havana': rdo_rhel_base + [rdo_havana]
        })
elif 'rhel-7' in common.DISTRIBUTION:
    combinations.update({
        'rdo-icehouse': rdo_rhel7_base + [rdo_icehouse],
        'upstream-icehouse': rdo_rhel7_base + [rdo_icehouse],
        'upstream-master': rdo_rhel7_base + [rdo_icehouse],
    })
elif 'fedora-19' in common.DISTRIBUTION:
    combinations.update({
        'rdo-havana': [rdo_havana_fedora],
        'rdo-havana_stage': [rdo_havana_stage_fedora],
        'upstream-master': [],
        'upstream-icehouse': [],
        'upstream-havana': [rdo_havana_fedora],
    })
elif 'fedora-20' in common.DISTRIBUTION:
    combinations.update({
        'rdo-havana': [],
        'rdo-icehouse': [rdo_icehouse],
        'rdo-icehouse_stage': [rdo_icehouse_stage_fedora],
        'upstream-master': [],
        'upstream-icehouse': [],
        'upstream-havana': []})
elif 'fedora-21' in common.DISTRIBUTION:
    combinations.update({
        'rdo-rawhide': [fedora_rawhide],
        'rdo-icehouse': [rdo_icehouse],
        'rdo-icehouse_stage': [rdo_icehouse_stage_fedora],
        'upstream-master': [],
        'upstream-icehouse': [],
        'upstream-havana': []})

all_repos = combinations[common.OS_VERSION]
