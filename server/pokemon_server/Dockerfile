FROM ubuntu:14.04

# RUN echo "\n\
# deb http://mirrors.163.com/debian/ jessie main contrib non-free\n\
# deb-src http://mirrors.163.com/debian jessie main contrib non-free\n\
# deb http://mirrors.163.com/debian/ jessie-proposed-updates main contrib non-free\n\
# deb-src http://mirrors.163.com/debian/ jessie-proposed-updates main contrib non-free\n\
# deb http://mirrors.163.com/debian/ jessie-updates main contrib non-free\n\
# deb-src http://mirrors.163.com/debian/ jessie-updates main contrib non-free\n\
# deb http://mirrors.163.com/debian-security/ jessie/updates main contrib non-free\n\
# deb-src http://mirrors.163.com/debian-security/ jessie/updates main contrib non-free\n"\
# > /etc/apt/sources.list
#

RUN echo "\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty-security main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty-updates main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty-proposed main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty-backports main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-security main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-updates main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-proposed main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-backports main restricted universe multiverse\n"\
> /etc/apt/sources.list


RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y -q python-dev python-pip git swig openssl libssl-dev libluajit-5.1-dev pkg-config openjdk-7-jdk

# Add user if uid not exist
ARG uid
ARG gid
RUN ["/bin/bash", "-c", "[[ \"`getent passwd $uid`\" ]] || groupadd -g $gid sandbox && useradd -u $uid -g sandbox sandbox -s /bin/bash"]

#
ADD requirements.txt requirements.txt
ADD pkgs pkgs
ADD protobuf.so /usr/local/lib/lua/5.1/

# FIX https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=733644
RUN ln -s /usr/include/x86_64-linux-gnu/openssl/opensslconf.h /usr/include/openssl/opensslconf.h

ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64
RUN pip install pkgs/Cython-0.20.1.tar.gz && pip install pkgs/M2Crypto-0.22.3.tar.gz && pip install pkgs/JPype-0.5.4.2.zip && pip install -r requirements.txt

# # FIX https://github.com/mistio/mist.io/issues/434
# RUN sed -i -e 's/PROTOCOL_SSLv3/PROTOCOL_SSLv23/g' /usr/local/lib/python2.7/site-packages/gevent/ssl.py

VOLUME ["/opt/src", "/opt/game"]
WORKDIR /opt/game
ENV PYTHONPATH /opt/src
