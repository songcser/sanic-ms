#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ujson
import unittest
import logging

from itertools import repeat
from multidict import CIMultiDict
from aiohttp import hdrs, ClientResponse, StreamReader
from sanic.views import CompositionView
from asyncpg import create_pool
from urllib.parse import urlparse, parse_qsl, urlencode

from sanic_ms.client import Client, ClientSessionConn
from sanic_ms.db import ConnectionPool

from sanic_ms.config import DB_CONFIG

logger = logging.getLogger('sanic')

try:
    from yarl import URL
except ImportError:
    class URL(str):
        pass

class MockResponse(object):
    resp = None

    def __init__(self, url, method = hdrs.METH_GET,
                 status = 200, body = '',
                 exception = None,
                 headers = None, payload = None,
                 content_type = 'application/json', ):
        self.url = self.parse_url(url)
        self.method = method.lower()
        self.status = status
        if payload is not None:
            body = ujson.dumps(payload)
        if not isinstance(body, bytes):
            body = str.encode(body)
        self.body = body
        self.exception = exception
        self.headers = headers
        self.content_type = content_type

    async def __aenter__(self):
        return self.build_response()

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def parse_url(self, url):
        """Normalize url to make comparisons."""
        _url = url.split('?')[0]
        query = urlencode(sorted(parse_qsl(urlparse(url).query)))
        return '{}?{}'.format(_url, query) if query else _url

    def match(self, method, url):
        if self.method != method.lower():
            return False
        return self.url == self.parse_url(url)

    def build_response(self):
        if isinstance(self.exception, Exception):
            raise self.exception
        self.resp = ClientResponse(self.method, URL(self.url))
        # we need to initialize headers manually
        self.resp.headers = CIMultiDict({hdrs.CONTENT_TYPE: self.content_type})
        if self.headers:
            self.resp.headers.update(self.headers)
        self.resp.status = self.status
        self.resp.content = StreamReader()
        self.resp.content.feed_data(self.body)
        self.resp.content.feed_eof()

        return self.resp

class MockClient(Client):

    def __init__(self, **kwargs):
        self._responses = []

    def cli(self, req):
        return MockClientSessionConn(self._responses)

    def close(self):
        pass

    def get(self, url, **kwargs):
        self.add(url, method=hdrs.METH_GET, **kwargs)

    def post(self, url, **kwargs):
        self.add(url, method=hdrs.METH_POST, **kwargs)

    def put(self, url, **kwargs):
        self.add(url, method=hdrs.METH_PUT, **kwargs)

    def patch(self, url, **kwargs):
        self.add(url, method=hdrs.METH_PATCH, **kwargs)

    def delete(self, url, **kwargs):
        self.add(url, method=hdrs.METH_DELETE, **kwargs)

    def options(self, url, **kwargs):
        self.add(url, method=hdrs.METH_OPTIONS, **kwargs)

    def add(self, url, method = hdrs.METH_GET, status = 200,
            body = '',
            exception = None,
            content_type = 'application/json',
            payload = None,
            headers = None):
        self._responses.append(MockResponse(
            url,
            method=method,
            status=status,
            content_type=content_type,
            body=body,
            exception=exception,
            payload=payload,
            headers=headers,
        ))



class MockClientSessionConn(ClientSessionConn):

    def __init__(self, res=None, **kwargs):
        self._responses = res

    def match(self, method: str, url: str):
        i, resp = next(
            iter(
                [(i, r.build_response())
                 for i, r in enumerate(self._responses)
                 if r.match(method, url)]
            ),
            (None, None)
        )

        #if i is not None:
        #    del self._responses[i]
        return resp

    def request(self, method, url, **kwargs):
        resp = self.match(method, url)
        return resp

    def close(self):
        pass


class TestAPIClient(object):

    def __init__(self, app, blueprint):
        self._app = app
        self._blueprint = blueprint
        self._url_map = {}
        for uri, route in app.router.routes_all.items():
            handler_type = type(route.handler)
            if handler_type is CompositionView:
                view = route.handler
                method_handlers = view.handlers.items()
            else:
                method_handlers = zip(route.methods, repeat(route.handler))
            for _method, _handler in method_handlers:
                self._url_map.update({
                    _handler.__name__: {'method': _method, 'url': uri,
                            'parameters': [p.name for p in route.parameters]}
                })

    def __getattr__(self, name):
        def request(**kwargs):
            #params = kwargs.pop('params', None)
            #data = kwargs.pop('data', None)
            #n = "%s.%s" % (self._blueprint, name) if self._blueprint else name
            #url = self._app.url_for(n, **kwargs)
            url_map = self._url_map[name]
            url, data, params = url_map['url'], {}, {}
            for k, v in kwargs.items():
                if k in url_map['parameters']:
                    string = "<%s:?\w*>" % k
                    url = re.sub(string, str(v), url)
                if k == 'data':
                    data = v
                if k == 'params':
                    params = v
            res = {}
            if 'GET' in url_map['method']:
                req, res = self._app.test_client.get(url, params=params)
            if 'POST' in url_map['method']:
                req, res = self._app.test_client.post(url, data=ujson.dumps(data), params=params)
            if 'PUT' in url_map['method']:
                req, res = self._app.test_client.put(url, data=ujson.dumps(data), params=params)
            if 'DELETE' in url_map['method']:
                req, res = self._app.test_client.delete(url, params=params)
            return res
        return request

class APITestCase(unittest.TestCase):
    _app = None
    _blueprint = None

    def setUp(self):
        super(APITestCase, self).setUp()
        self._mock = MockClient()
        @self._app.listener('before_server_start')
        async def set_mock_client(app, loop):
            if app.client:
                app.client.close()
            app.client = self._mock
            app.db = await ConnectionPool(loop=loop).init(DB_CONFIG)
        self.client = TestAPIClient(self._app, self._blueprint)

    def tearDown(self):
        super(APITestCase, self).tearDown()
