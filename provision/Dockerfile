FROM rhel68-new
MAINTAINER Eko "hsun@redhat.com"

RUN wget http://10.66.144.9/home/shihliu/satellite62.repo

RUN mv satellite62.repo /etc/yum.repos.d/

RUN subscription-manager repos --disable "*"
RUN subscription-manager repos --enable rhel-6-server-rpms --enable=rhel-6-server-optional-rpms --enable rhel-server-rhscl-6-rpms

RUN yum install -y satellite
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]


