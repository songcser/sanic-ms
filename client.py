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
        return self._client

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    def close(self):
        self._client.close()
