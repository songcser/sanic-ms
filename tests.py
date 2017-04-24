#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import ujson
import unittest
import logging

from server import app

logger = logging.getLogger('sanic')

class TestAPIClient(object):

    def __init__(self, app, blueprint):
        self._app = app
        self._router = app.router.routes_all
        self._blueprint = blueprint
        self._url_map = {}
        for k, v in self._router.items():
            self._url_map.update({
                v.name: {'method': v.methods, 'url': k,
                         'parameters': [p.name for p in v.parameters]}
            })

    def __getattr__(self, name):
        def request(**kwargs):
            if self._blueprint:
                n = "%s.%s" % (self._blueprint, name)
            url_map = self._url_map[n]
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
        self.client = TestAPIClient(self._app, self._blueprint)

    def tearDown(self):
        super(APITestCase, self).tearDown()
