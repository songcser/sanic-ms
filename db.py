#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from asyncpg import connect, create_pool
from ethicall_common.utils import jsonify


logger = logging.getLogger('sanic')

class BaseConnection(object):
    def __init__(self, pool):
        self._pool = pool
        self.conn = None

    @property
    def rowcount(self):
        return self.conn.rowcount

    async def add_listener(self, channel, callback):
        await self.conn.add_listener(channel, callback)

    async def remove_listener(self, channel, callback):
        await self.conn.remove_listener(channel, callback)

    async def execute(self, query:str, *args, timeout:float=None):
        return await self.conn.execute(query, *args, timeout=timeout)

    async def executemany(self, command:str, args, timeout:float=None):
        return await self.conn.executemmay(command, args, timeout=timeout)

    async def fetch(self, query, *args, timeout=None):
        return jsonify(await self.conn.fetch(query, *args, timeout=timeout))

    async def fetchrow(self, query, *args, timeout=None):
        return dict(await self.conn.fetchrow(query, *args, timeout=timeout))

    async def fetchval(self, query, *args, column=0, timeout=None):
        return await self.conn.fetchval(query, *args, column=column, timeout=timeout)

    async def prepare(self, query, *args, timeout=None):
        return await self.conn.prepare(query, *args, timeout=None)

    async def set_builtin_type_codec(self, typename, *args, schema='public', codec_name):
        await self.conn.set_builtin_type_codec(typename, *args, schema=schema, codec_name=codec_name)

    async def set_type_codec(self, typename, *args, schema='public', encoder, decoder, binary=False):
        await self.conn.set_type_codec(typename, *args, schema=schema, encoder=encoder, decoder=decoder, binary=binary)

    def transaction(self, *args, isolation='read_committed', readonly=False, deferrable=False):
        return self.conn.transaction(*args, isolation=isolation, readonly=readonly, deferrable=deferrable)

    async def release(self):
        await self._pool.release(self.conn)

    async def close(self):
        await self.conn.close()

    async def __aenter__(self):
        self.conn = await self._pool.acquire()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.release()

class TransactionConnection(BaseConnection):
    def __init__(self, pool):
        super(TransactionConnection, self).__init__(pool)

    async def __aenter__(self):
        self.conn = await self._pool.acquire()
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

class ConnectionPool(object):
    PGHOST = None
    PGUSER = None
    PGPASSWORD = None
    PGPORT = None
    PGDATABASE = None
    pool = None

    def __init__(self, loop=None):
        self.conn = None
        self._loop = loop
        self._pool = None

    async def init(self, DB_CONFIG):
        self._pool = await create_pool(**DB_CONFIG, loop=self._loop, max_size=100)
        return self

    def acquire(self):
        return BaseConnection(self._pool)

    def transaction(self):
        return TransactionConnection(self._pool)
