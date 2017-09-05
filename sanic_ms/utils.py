#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import asyncio

logger = logging.getLogger('sanic')

PAGE_COUNT = 20

def jsonify(records):
    """
    Parse asyncpg record response into JSON format
    """
    return [dict(r.items()) for r in records]

async def async_request(calls):
    results = await asyncio.gather(*[ call[2] for call in calls])
    for index, obj in enumerate(results):
        call = calls[index]
        call[0][call[1]] = results[index]

async def async_execute(*calls):
    results = await asyncio.gather(*calls)
    return tuple(results)

def id_to_hex(id):
    if id is None:
        return None
    return '{0:x}'.format(id)
