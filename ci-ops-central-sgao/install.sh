#!/bin/bash


if grep -q 'Red Hat Enterprise Linux' /etc/redhat-release; then
    # Determine Version of RHEL
    export MAJOR_VER=$(egrep ' 6| 7' /etc/redhat-release | awk '{print $7}' | cut -d. -f1)
    export MINOR_VER=$(egrep ' 6| 7' /etc/redhat-release | awk '{print $7}')
    if [[ ! -f /etc/yum.repos.d/epel.repo ]]; then
        if [[ "$MAJOR_VER" == "6" ]]; then
            wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
            sudo rpm -Uvh epel-release-6*.rpm
    elif [[ "$MAJOR_VER" == "7" ]]; then
            wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
            sudo rpm -Uvh epel-release-7*.rpm
        else
            echo "Don't know which epel to use!"
        fi
    fi

    if [ "$MAJOR_VER" == "6" ]; then
        echo -n "Release and Optional Repos"
        export RHEL_RELEASE=http://download.eng.bos.redhat.com/released/RHEL-$MAJOR_VER/$MINOR_VER/Server/x86_64/os/
        export RHEL_OPTIONAL=http://download.lab.bos.redhat.com/rel-eng/latest-RHEL-$MAJOR_VER/$MAJOR_VER/Server/optional/x86_64/os/
        export PKG_LIST='git wget python-unittest2 python-nose python-futures python-paramiko python-lxml python-six python-configobj python-pip python-argparse
gcc compat-gcc-34.x86_64 libffi-devel python-devel openssl-devel libxml2-devel libxslt-devel
graphviz lftp krb5-workstation ansible'
        echo "RHEL_RELEASE = $RHEL_RELEASE"
        echo "RHEL_OPTIONAL = $RHEL_OPTIONAL"
        echo "PKG_LIST = $PKG_LIST"
    elif [ "$MAJOR_VER" == "7" ]; then
        echo -n "Release and Optional Repos"
        if [[ "$MINOR_VER" == "7.0" ]]; then
            export RHEL_RELEASE=http://download.eng.bos.redhat.com/released/RHEL-$MAJOR_VER/7.0/Server/x86_64/os/
        else
            export RHEL_RELEASE=http://download.eng.bos.redhat.com/released/RHEL-$MAJOR_VER/7.1-Beta/Server/x86_64/os/
        fi
        export RHEL_OPTIONAL=http://download.lab.bos.redhat.com/rel-eng/latest-RHEL-$MAJOR_VER/compose/Server-optional/x86_64/os/
        export PKG_LIST='git wget python-unittest2 python-nose python-futures python-paramiko python-lxml python-six python-configobj python-pip python-argparse
gcc compat-gcc-34.x86_64 libffi-devel python-devel openssl-devel libxml2-devel libxslt-devel
graphviz lftp krb5-workstation ansible'
        echo "RHEL_RELEASE = $RHEL_RELEASE"
        echo "RHEL_OPTIONAL = $RHEL_OPTIONAL"
        echo "PKG_LIST = $PKG_LIST"
    fi

    ## Installing the RHEL released repo
    if [[ ! -f /etc/yum.repos.d/rhel${MAJOR_VER}-released.repo ]]; then
        echo -n "Installing rhel${MAJOR_VER}-released.repo"
sudo cat > /etc/yum.repos.d/rhel${MAJOR_VER}-released.repo << EOF
[rhel${MAJOR_VER}-released]
name=rhel${MAJOR_VER}-released
baseurl=$RHEL_RELEASE
skip_if_unavailable=0
enabled=1
sslverify=0
gpgcheck=0
EOF
       if [ $? == 0 ]; then
           echo "...PASSED"
       else
           echo "...FAILED"
       fi
    fi

    ## Installing the RHEL optional repo
    if [[ ! -f /etc/yum.repos.d/rhel${MAJOR_VER}-optional.repo ]]; then
        echo -n "Installing rhel${MAJOR_VER}-optional.repo"
sudo cat > /etc/yum.repos.d/rhel${MAJOR_VER}-optional.repo << EOF
[rhel${MAJOR_VER}-optional]
name=rhel${MAJOR_VER}-optoinal
baseurl=$RHEL_OPTIONAL
skip_if_unavailable=0
enabled=1
sslverify=0
gpgcheck=0
EOF
       if [ $? == 0 ]; then
           echo "...PASSED"
       else
           echo "...FAILED"
       fi
    fi

    ## Installing the RHEL extras repo
    if [[ ! -f /etc/yum.repos.d/rhel${MAJOR_VER}-extras.repo ]]; then
        echo -n "Installing rhel${MAJOR_VER}-extras.repo"
sudo cat > /etc/yum.repos.d/rhel${MAJOR_VER}-extras.repo << EOF
[rhel${MAJOR_VER}-extras]
name=rhel${MAJOR_VER}-extras
baseurl=http://download.eng.bos.redhat.com/rel-eng/latest-EXTRAS-$MAJOR_VER-RHEL-$MAJOR_VER/compose/Server/x86_64/os/
skip_if_unavailable=0
enabled=1
sslverify=0
gpgcheck=0
EOF
       if [ $? == 0 ]; then
           echo "...PASSED"
       else
           echo "...FAILED"
       fi
    fi

    ## Installing the RH OSP repo
    if [ "$MAJOR_VER" == "6" ]; then
        echo -n "Installing rh-osp4.repo"
sudo cat > /etc/yum.repos.d/rh-osp4.repo << EOF
[rh-osp4]
name=rh-osp4
baseurl=http://download.lab.bos.redhat.com/rel-eng/OpenStack/4.0/latest/RHOS-4.0/\$basearch/os/
skip_if_unavailable=0
enabled=1
sslverify=0
gpgcheck=0
EOF
       if [ $? == 0 ]; then
           echo "...PASSED"
       else
           echo "...FAILED"
       fi
    fi

   ## Install libxslt-python
    if [ "`rpm -qa | grep libxslt-python`" == "" ]; then
       echo -n "Installing libxslt-python ... "
       sudo yum install -y libxslt-python
       if [ $? == 0 ]; then
           echo "...PASSED"
       else
           echo "...FAILED"
       fi
    fi

    ## Install Beaker client
    if [ "`rpm -qa | grep beaker-client`" == "" ]; then
       echo -n "Installing Beaker Client ... "
       sudo curl -o /etc/yum.repos.d/beaker-client-RedHatEnterpriseLinux.repo https://beaker-project.org/yum/beaker-client-RedHatEnterpriseLinux.repo
       sudo yum install -y beaker-client
       if [ $? == 0 ]; then
           echo "...PASSED"
       else
           echo "...FAILED"
       fi
    fi
elif grep -q 'Fedora' /etc/redhat-release; then
    export PKG_LIST='git wget python-unittest2 python-nose python-futures python-paramiko python-lxml python-six python-configobj python-pip python-argparse
gcc compat-gcc-34.x86_64 libffi-devel python-devel openssl-devel libxml2-devel libxslt-devel
graphviz lftp krb5-workstation ansible'

    ## Install libxslt-python
    if [ "`rpm -qa | grep libxslt-python`" == "" ]; then
       echo -n "Installing libxslt-python ... "
       sudo yum install -y libxslt-python
       if [ $? == 0 ]; then
           echo "...PASSED"
       else
           echo "...FAILED"
       fi
    fi

    ## Install Beaker client
    if [ "`rpm -qa | grep beaker-client`" == "" ]; then
       echo -n "Installing Beaker Client ... "
       sudo curl -o /etc/yum.repos.d/beaker-client-Fedora.repo https://beaker-project.org/yum/beaker-client-Fedora.repo
       sudo yum install -y beaker-client
       if [ $? == 0 ]; then
           echo "...PASSED"
       else
           echo "...FAILED"
       fi
    fi
fi

cd $(dirname $(readlink -f $0))

set -o errexit
set -x

sudo yum install -y $PKG_LIST

pip --version
if [ $? != 0 ]; then
    if [[ "$MAJOR_VER" == "7" ]] || grep -q 'Fedora' /etc/redhat-release; then
        echo "Installing PIP for RHEL7"
        wget https://pypi.python.org/packages/source/s/setuptools/setuptools-7.0.tar.gz --no-check-certificate
        tar xzf setuptools-7.0.tar.gz
        cd setuptools-7.0
        python setup.py install
        wget https://bootstrap.pypa.io/get-pip.py
        python get-pip.py
    fi
fi
pip install taskrunner python-{keystone,glance,nova}client python-foreman jenkins-job-builder==1.1.0

cd $(dirname $(readlink -f $0))

cd ..
[[ -d job-runner ]] || git clone git://git.app.eng.bos.redhat.com/job-runner.git
# CI central project example
[[ -d ci-ops-projex ]] || git clone git://git.app.eng.bos.redhat.com/ci-ops-projex.git

