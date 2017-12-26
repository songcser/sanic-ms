#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import logging.config
import datetime
import yaml
import aiohttp
import os
import opentracing

from basictracer import BasicTracer

from sanic import Sanic, config
from sanic.response import json, text, HTTPResponse
from sanic.exceptions import RequestTimeout, NotFound
from aiohttp import ClientSession

from sanicms.config import DB_CONFIG, ZIPKIN_SERVER
from sanicms.db import ConnectionPool
from sanicms.client import Client
from sanicms.utils import *
from sanicms.loggers import AioReporter
from sanicms.openapi import blueprint as openapi_blueprint

with open(os.path.join(os.path.dirname(__file__), 'logging.yml'), 'r') as f:
    logging.config.dictConfig(yaml.load(f))

app = Sanic(__name__, error_handler=CustomHandler())
app.config.ZIPKIN_SERVER = ZIPKIN_SERVER
app.blueprint(openapi_blueprint)


@app.listener('before_server_start')
async def before_srver_start(app, loop):
    queue = asyncio.Queue()
    app.queue = queue
    loop.create_task(consume(queue, app.config.ZIPKIN_SERVER))
    reporter = AioReporter(queue=queue)
    tracer = BasicTracer(recorder=reporter)
    tracer.register_required_propagators()
    opentracing.tracer = tracer
    app.db = await ConnectionPool(loop=loop).init(DB_CONFIG)


@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    app.queue.join()


@app.middleware('request')
async def cros(request):
    if request.method == 'POST' or request.method == 'PUT':
        request['data'] = request.json
    span = before_request(request)
    request['span'] = span


@app.middleware('response')
async def cors_res(request, response):
    span = request['span'] if 'span' in request else None
    if response is None:
        return response
    result = {'code': 0}
    if not isinstance(response, HTTPResponse):
        if isinstance(response, tuple) and len(response) == 2:
            result.update({
                'data': response[0],
                'pagination': response[1]
            })
        else:
            result.update({'data': response})
        response = json(result)
        if span:
            span.set_tag('http.status_code', "200")
    if span:
        span.set_tag('component', request.app.name)
        span.finish()
    return response


@app.exception(RequestTimeout)
def timeout(request, exception):
    return json({'message': 'Request Timeout'}, 408)


@app.exception(NotFound)
def notfound(request, exception):
    return json(
        {'message': 'Requested URL {} not found'.format(request.url)}, 404)
