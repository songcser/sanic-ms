#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from asyncpg import connect, create_pool


logger = logging.getLogger('sanic')

class BaseConnection(object):
    PGHOST = None
    PGUSER = None
    PGPASSWORD = None
    PGPORT = None
    PGDATABASE = None
    pool = None

    def __init__(self, loop=None):
        self.cursor = None
        self._loop = loop

    @property
    def rowcount(self):
        return self.cursor.rowcount

    async def create_connection(self):
        self.cursor = await self._pool.acquire()
        return self

    def acquire(self):
        return self._pool.acquire()

    async def init(self, DB_CONFIG):
        self._pool = await create_pool(**DB_CONFIG, loop=self._loop, max_size=100)
        return self

    async def add_listener(self, channel, callback):
        await self.cursor.add_listener(channel, callback)

    async def remove_listener(self, channel, callback):
        await self.cursor.remove_listener(channel, callback)

    async def execute(self, query:str, *args, timeout:float=None):
        return await self.cursor.execute(query, *args, timeout=timeout)

    async def executemany(self, command:str, args, timeout:float=None):
        return await self.cursor.executemmay(command, args, timeout=timeout)

    async def fetch(self, query, *args, timeout=None):
        return await self.cursor.fetch(query, *args, timeout=timeout)

    async def fetchrow(self, query, *args, timeout=None):
        return await self.cursor.fetchrow(query, *args, timeout=timeout)

    async def fetchval(self, query, *args, column=0, timeout=None):
        return await self.cursor.fetchval(query, *args, column=column, timeout=timeout)

    async def prepare(self, query, *args, timeout=None):
        return await self.cursor.prepare(query, *args, timeout=None)

    async def set_builtin_type_codec(self, typename, *args, schema='public', codec_name):
        await self.cursor.set_builtin_type_codec(typename, *args, schema=schema, codec_name=codec_name)

    async def set_type_codec(self, typename, *args, schema='public', encoder, decoder, binary=False):
        await self.cursor.set_type_codec(typename, *args, schema=schema, encoder=encoder, decoder=decoder, binary=binary)

    def transaction(self, *args, isolation='read_committed', readonly=False, deferrable=False):
        return self.cursor.transaction(*args, isolation=isolation, readonly=readonly, deferrable=deferrable)

    async def close(self):
        await self.cursor.close()

    async def release(self):
        await self._pool.release(self.cursor)

    async def closeAll(self):
        await self._pool.close()

    async def __aenter__(self):
        await self.create_connection()
        self.tr = self.transaction()
        await self.tr.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                await self.tr.commit()
            else:
                await self.tr.rollback()
        except:
            pass
        finally:
            await self.release()
