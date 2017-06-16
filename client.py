#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import ClientSession

class Client:
    _client = None

    def __init__(self, loop, url=None):
        self._client = ClientSession(loop=loop)
        self._url = url

    @property
    def cli(self):
        return self._client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    def handler_url(self, url):
        if url.startswith("http"):
            return url
        if self._url:
            return "{}{}".format(self._url, url)
        return url

    def request(self, method, url, *args, **kwargs):
        return self._client.request(method, self.handler_url(url), *args, **kwargs)

    def get(self, url, allow_redirects=True, **kwargs):
        return self._client.get(self.handler_url(url), allow_redirects=True, **kwargs)

    def post(self, url, data=None, **kwargs):
        return self._client.post(self.handler_url(url), data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self._client.put(self.handler_url(url), data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self._client.delete(self.handler_url(url), **kwargs)

    def head(self, url, allow_redirects=False, **kwargs):
        return self._client.head(self.handler_url(url), allow_redirects=allow_redirects, **kwargs)

    def options(self, url, allow_redirects=True, **kwargs):
        return self._client.options(self.handler_url(url), allow_redirects=allow_redirects, **kwargs)

    def close(self):
        self._client.close()
