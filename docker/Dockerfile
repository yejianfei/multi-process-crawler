# This is a comment
from ubuntu:15.04
maintainer yejianfei <yejianfei.billy@gmail.com>

run mv /etc/apt/sources.list /etc/apt/sources.list.org && echo "\
deb http://mirrors.aliyun.com/ubuntu/ vivid main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ vivid-security main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ vivid-updates main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ vivid-proposed main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ vivid-backports main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ vivid main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ vivid-security main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ vivid-updates main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ vivid-proposed main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ vivid-backports main restricted universe multiverse\n\
" > /etc/apt/sources.list && \
apt-get update && \
apt-get dist-upgrade && \
apt-get install -y python python-pip python-dev libevent-dev python-setuptools git ssh apt-utils && \
mkdir -p /root/.pip && \
echo "\
[global]\n\
trusted-host = mirrors.aliyun.com\n\
index-url = http://mirrors.aliyun.com/pypi/simple/\n\
" > /root/.pip/pip.conf && \
pip install --upgrade pip && \
pip install gevent && \
pip install gunicorn && \
cd /opt && git clone https://github.com/yejianfei/multi-process-crawler.git && \
pip install -r multi-process-crawler/requirements.txt

workdir /opt/multi-process-crawler
expose 9000 9001
entrypoint ["/opt/multi-process-crawler/docker/entrypoint"]