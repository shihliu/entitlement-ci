FROM registry.access.redhat.com/rhel6.8:latest
MAINTAINER Eko "hsun@redhat.com"

RUN subscription-manager register --username=qa@redhat.com --password=8pf87qhuF8Eg9MPq --auto-attach
RUN yum install -y openssh-server net-tools hostname sudo
RUN yum install -y java
RUN yum install -y python-nose
RUN yum install -y python-paramiko
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

