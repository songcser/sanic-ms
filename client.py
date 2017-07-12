#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import opentracing
from aiohttp import ClientSession
from ethicall_common.loggers import AioReporter

logger = logging.getLogger('sanic')

class Client:

    def __init__(self, loop=None, url=None, **kwargs):
        self._client = ClientSession(loop=loop, **kwargs)
        self._url = url

    def cli(self, req):
        span = opentracing.tracer.start_span(operation_name='get', child_of=req['span'])
        return ClientConn(self._client, url=self._url, span=span,
                      reporter=req.app.reporter)

    def close(self):
        self._client.close()


class ClientConn:
    _client = None

    def __init__(self, client, url=None, span=None, reporter=None, **kwargs):
        self._client = client
        self._url = url
        self._span = span
        self._reporter = reporter

    @property
    def cli(self):
        return self._client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._reporter.finish('http-client', self._span)

    def handler_url(self, url):
        if url.startswith("http"):
            return url
        if self._url:
            return "{}{}".format(self._url, url)
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


    def request(self, method, url, *args, **kwargs):
        headers = self.before(method, url)
        return self._client.request(method, self.handler_url(url),
                                    headers=headers, *args, **kwargs)

    def get(self, url, allow_redirects=True, **kwargs):
        headers = self.before('GET', url)
        return self._client.get(self.handler_url(url), allow_redirects=True,
                                headers=headers, **kwargs)

    def post(self, url, data=None, **kwargs):
        headers = self.before('POST', url)
        return self._client.post(self.handler_url(url), data=data,
                                 headers=headers, **kwargs)

    def put(self, url, data=None, **kwargs):
        headers = self.before('PUT', url)
        return self._client.put(self.handler_url(url), data=data,
                                headers=headers, **kwargs)

    def delete(self, url, **kwargs):
        headers = self.before('DELETE', url)
        return self._client.delete(self.handler_url(url), headers=headers, **kwargs)

    def head(self, url, allow_redirects=False, **kwargs):
        headers = self.before('HEAD', url)
        return self._client.head(self.handler_url(url), headers=headers,
                                 allow_redirects=allow_redirects, **kwargs)

    def options(self, url, allow_redirects=True, **kwargs):
        headers = self.before('OPTIONS', url)
        return self._client.options(self.handler_url(url), headers=headers,
                                    allow_redirects=allow_redirects, **kwargs)

    def close(self):
        self._client.close()
