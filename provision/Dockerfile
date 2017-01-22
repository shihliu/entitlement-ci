FROM registry.access.redhat.com/rhel6.8:latest
MAINTAINER "shihliu@redhat.com"

RUN subscription-manager register --username=qa@redhat.com --password=asvTG7FQQNJQt5cV --auto-attach
RUN yum install -y openssh-server net-tools hostname sudo
RUN yum install -y java
RUN yum install -y python-paramiko python-nose
RUN yum install -y python-requests
#RUN rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
#RUN yum install -y python-pip
#RUN pip install nose
RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
RUN echo "root:red2015" | chpasswd
RUN ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key

RUN yum install -y wget
RUN yum install -y git

VOLUME ["/sys/fs"]
VOLUME ["/run"]
VOLUME ["/export"]

RUN mkdir /var/run/sshd
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

