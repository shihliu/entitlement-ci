FROM rhel6.8:latest
MAINTAINER Eko "hsun@redhat.com"
#RUN tar xzvf satellite_docker.tar.gz 
RUN cp $WORKSPACE/entitlement-ci/data/satellite62.repo /etc/yum.repos.d/
RUN subscription-manager repos --disable "*"
RUN subscription-manager repos --enable rhel-6-server-rpms --enable=rhel-6-server-optional-rpms --enable rhel-server-rhscl-6-rpms
#RUN yum install -y wget

#RUN cd /etc/yum.repos.d/
#
#RUN wget http://10.66.144.9/home/shihliu/satellite62.repo
#
#RUN mv satellite62.repo /etc/yum.repos.d/
#
#RUN mkdir /var/run/sshd
#EXPOSE 22
#CMD ["/usr/sbin/sshd", "-D"]
