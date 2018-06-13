#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import logging.config
import datetime
import yaml
import os
import opentracing

from basictracer import BasicTracer

from sanic import Sanic, config
from sanic.response import json, text, HTTPResponse
from sanic.exceptions import RequestTimeout, NotFound
from aiohttp import ClientSession

from sanicms import load_config
from sanicms.db import ConnectionPool
from sanicms.client import Client
from sanicms.utils import *
from sanicms.loggers import AioReporter
from sanicms.openapi import blueprint as openapi_blueprint
from sanicms.service import Service

with open(os.path.join(os.path.dirname(__file__), 'logging.yml'), 'r') as f:
    logging.config.dictConfig(yaml.load(f))

config = load_config()
appid = config.get('APP_ID', __name__)
app = Sanic(appid, error_handler=CustomHandler())
app.config = config
app.blueprint(openapi_blueprint)


@app.listener('before_server_start')
async def before_srver_start(app, loop):
    queue = asyncio.Queue()
    app.queue = queue
    loop.create_task(consume(queue, app.config['ZIPKIN_SERVER']))
    reporter = AioReporter(queue=queue)
    tracer = BasicTracer(recorder=reporter)
    tracer.register_required_propagators()
    opentracing.tracer = tracer
    app.db = await ConnectionPool(loop=loop).init(app.config['DB_CONFIG'])


@app.listener('after_server_start')
async def after_server_start(app, loop):
    service = Service(app.name, loop=loop)
    await service.register_service(app.config['PORT'])
    app.service = service


@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    await app.servcie.deregister(app.service.servcie_id)
    app.queue.join()


@app.middleware('request')
async def cros(request):
    config = request.app.config
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': config['ACCESS_CONTROL_ALLOW_ORIGIN'],
            'Access-Control-Allow-Headers': config['ACCESS_CONTROL_ALLOW_HEADERS'],
            'Access-Control-Allow-Methods': config['ACCESS_CONTROL_ALLOW_METHODS']
        }
        return json({'code': 0}, headers=headers)
    if request.method == 'POST' or request.method == 'PUT':
        request['data'] = request.json
    span = before_request(request)
    request['span'] = span


@app.middleware('response')
async def cors_res(request, response):
    config = request.app.config
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
    response.headers["Access-Control-Allow-Origin"] = config['ACCESS_CONTROL_ALLOW_ORIGIN']
    response.headers["Access-Control-Allow-Headers"] = config['ACCESS_CONTROL_ALLOW_HEADERS']
    response.headers["Access-Control-Allow-Methods"] = config['ACCESS_CONTROL_ALLOW_METHODS']
    return response


@app.exception(RequestTimeout)
def timeout(request, exception):
    return json({'message': 'Request Timeout'}, 408)


@app.exception(NotFound)
def notfound(request, exception):
    return json(
        {'message': 'Requested URL {} not found'.format(request.url)}, 404)
