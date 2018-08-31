#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import logging
import opentracing
from aiohttp import ClientSession, hdrs

logger = logging.getLogger('sanic')


class Client:

    def __init__(self, name, app=None, url=None, client=None, **kwargs):
        self.name = name
        self._client = client if client else ClientSession(loop=app.loop, **kwargs)
        self.services = app.services[self.name]
        self._url = url

    def handler_url(self):
        if self._url:
            return
        if self.services:
            s = random.choice(self.services)
            self._url = 'http://{}:{}'.format(s.service_address, s.service_port)

    def cli(self, req):
        self.handler_url()
        span = opentracing.tracer.start_span(operation_name='get', child_of=req['span'])
        return ClientSessionConn(self._client, url=self._url, span=span)

    def close(self):
        self._client.close()


class ClientSessionConn:
    _client = None

    def __init__(self, client, url=None, span=None, **kwargs):
        self._client = client
        self._url = url
        self._span = span

    def handler_url(self, url):
        if url.startswith("http"):
            return url
        if self._url:
            return "{}/{}".format(self._url, url)
        return url

    def before(self, method, url):
        self._span.log_kv({'event': 'client'})
        self._span.set_tag('http.url', self._url)
        self._span.set_tag('http.path', url)
        self._span.set_tag('http.method', method)
        http_header_carrier = {}
        opentracing.tracer.inject(
            self._span.context,
            format=opentracing.Format.HTTP_HEADERS,
            carrier=http_header_carrier)
        return http_header_carrier


    def request(self, method, url, **kwargs):
        headers = self.before(method, url)
        res = self._client.request(method, self.handler_url(url),
                                   headers=headers, **kwargs)
        self._span.set_tag('component', 'http-client')
        self._span.finish()
        return res

    def get(self, url, allow_redirects=True, **kwargs):
        return self.request(hdrs.METH_GET, url, allow_redirects=True,
                       **kwargs)

    def post(self, url, data=None, **kwargs):
        return self.request(hdrs.METH_POST, url, data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.request(hdrs.METH_PUT, url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request(hdrs.METH_DELETE, url, **kwargs)

    def head(self, url, allow_redirects=False, **kwargs):
        return self.request(hdrs.METH_HEAD, url, allow_redirects=allow_redirects, **kwargs)

    def options(self, url, allow_redirects=True, **kwargs):
        return self.request(hdrs.METH_OPTIONS, url, allow_redirects=allow_redirects, **kwargs)

    def close(self):
        self._client.close()
