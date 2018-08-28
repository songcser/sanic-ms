FROM python:3.6-alpine3.6
MAINTAINER songjiyi2008@163.com

ADD . /service
WORKDIR /service

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
RUN apk add --no-cache gcc libc-dev git make postgresql-dev \
    && pip install -i 'http://pypi.douban.com/simple' --trusted-host pypi.douban.com -r requirements.txt \
    &&rm -rf /var/cache/apk/* /tmp/* /var/tmp/* $HOME/.cache

EXPOSE 8000
