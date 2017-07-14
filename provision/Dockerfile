FROM registry.access.redhat.com/rhel6.8:latest
MAINTAINER "shihliu@redhat.com"

# Register, subscribe and Install packages
RUN subscription-manager register --username=QualityAssurance --password=VHVFhPS5TEG8dud9 --auto-attach
RUN yum install -y openssh-server net-tools wget hostname sudo
RUN yum install -y java
RUN yum install -y python-paramiko python-nose
RUN yum install -y python-requests
RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
RUN echo "root:red2015" | chpasswd
RUN ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
RUN yum install -y wget
RUN yum install -y git

# Update nosetest to make it run with -xunit
RUN rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
RUN yum install -y python-pip python-unittest2
RUN yum update python-nose
RUN pip install --upgrade nose
# Update paramiko to make it with esx6.5
RUN yum install -y gcc openssl-devel python-devel
RUN pip install --upgrade pip
#RUN pip install --upgrade paramiko

VOLUME ["/sys/fs"]
VOLUME ["/run"]
VOLUME ["/export"]

RUN mkdir /var/run/sshd
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

