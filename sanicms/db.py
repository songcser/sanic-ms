#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import opentracing

from asyncpg import create_pool
from sanicms.utils import jsonify


logger = logging.getLogger('sanic')

class BaseConnection(object):
    def __init__(self, pool, span=None, conn=None):
        self._pool = pool
        self._span = span
        self.conn = conn

    @property
    def rowcount(self):
        return self.conn.rowcount

    def before(self, name, query, *args):
        if self._span:
            span = opentracing.tracer.start_span(operation_name=name, child_of=self._span)
            span.log_kv({ 'event': 'client'})
            span.set_tag('component', 'db-execute')
            span.set_tag('db.type', 'sql')
            span.set_tag('db.sql', query)
            span.set_tag('args', ','.join([str(a) for a in args]))
            return span

    def finish(self, span):
        if span: span.finish()

    async def add_listener(self, channel, callback):
        await self.conn.add_listener(channel, callback)

    async def remove_listener(self, channel, callback):
        await self.conn.remove_listener(channel, callback)

    async def execute(self, query:str, *args, timeout:float=None):
        span = self.before('execute', query, *args)
        res = await self.conn.execute(query, *args, timeout=timeout)
        self.finish(span)
        return res

    async def executemany(self, command:str, args, timeout:float=None):
        span = self.before('executemany', command, args)
        res = await self.conn.executemmay(command, args, timeout=timeout)
        self.finish(span)
        return res

    async def fetch(self, query, *args, timeout=None):
        span = self.before('fetch', query, *args)
        res = jsonify(await self.conn.fetch(query, *args, timeout=timeout))
        self.finish(span)
        return res

    async def fetchrow(self, query, *args, timeout=None):
        span = self.before('fetchrow', query, *args)
        res = dict(await self.conn.fetchrow(query, *args, timeout=timeout))
        self.finish(span)
        return res

    async def fetchval(self, query, *args, column=0, timeout=None):
        span = self.before('fetchval', query, *args)
        res = await self.conn.fetchval(query, *args, column=column, timeout=timeout)
        self.finish(span)
        return res

    async def prepare(self, query, *args, timeout=None):
        span = self.before('prepare', query, *args)
        res = await self.conn.prepare(query, *args, timeout=None)
        self.finish(span)
        return res

    async def set_builtin_type_codec(self, typename, *args, schema='public', codec_name):
        span = self.before('set_builtin_type_codec', typename, *args)
        await self.conn.set_builtin_type_codec(typename, *args, schema=schema, codec_name=codec_name)
        self.finish(span)

    async def set_type_codec(self, typename, *args, schema='public', encoder, decoder, binary=False):
        span = self.before('set_type_codec', typename, *args)
        await self.conn.set_type_codec(typename, *args, schema=schema, encoder=encoder, decoder=decoder, binary=binary)
        self.finish(span)

    def transaction(self, *args, isolation='read_committed', readonly=False, deferrable=False):
        return self.conn.transaction(*args, isolation=isolation, readonly=readonly, deferrable=deferrable)

    async def release(self):
        await self._pool.release(self.conn)

    async def close(self):
        await self.conn.close()

    async def __aenter__(self):
        self.conn = await self._pool.acquire() if not self.conn else self.conn
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.release()

class TransactionConnection(BaseConnection):
    def __init__(self, pool, span=None, conn=None):
        super(TransactionConnection, self).__init__(pool, span)
        self.conn = conn

    async def __aenter__(self):
        self.conn = await self._pool.acquire() if not self.conn else self.conn
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

    async def init(self, config, conn=None):
        if conn:
            self.conn = conn
        self._pool = await create_pool(**config, loop=self._loop, max_size=100)
        return self

    def acquire(self, request=None):
        return BaseConnection(self._pool, span=request['span'] if request else None)

    def transaction(self, request=None):
        return TransactionConnection(
            self._pool,
            span=request['span'] if request else None,
            conn=self.conn
        )
