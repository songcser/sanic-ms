#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import random
import logging
import logging.config
import datetime
import yaml
import aiohttp
#import queue
import opentracing
from opentracing.ext import tags
from basictracer import BasicTracer

from sanic import Sanic
from sanic.handlers import ErrorHandler
from sanic.response import json, text, HTTPResponse
from sanic.exceptions import RequestTimeout, NotFound
from aiohttp import ClientSession

from config import DB_CONFIG
from ethicall_common.db import ConnectionPool
from ethicall_common.client import Client
from ethicall_common.utils import jsonify
from ethicall_common.exception import CustomException
from ethicall_common.loggers import AioReporter
from ethicall_common.openapi import blueprint as openapi_blueprint
#from ethicall_common.swagger import blueprint as swagger_blueprint
from . import utils

with open('ethicall_common/logging.yml') as f:
    logging.config.dictConfig(yaml.load(f))

logger = logging.getLogger('sanic')
# make app
app = Sanic(__name__)
app.config.ZIPKIN_SERVER = ""

app.blueprint(openapi_blueprint)
#app.blueprint(swagger_blueprint)

class CustomHandler(ErrorHandler):

    def default(self, request, exception):
        if isinstance(exception, CustomException):
            data = {
                'message': exception.message,
                'code': exception.code,
            }
            if exception.error:
                data.update({'error': exception.error})
            span = request['span']
            span.set_tag('http.status_code', str(exception.status_code))
            span.set_tag('error.kind', exception.__class__.__name__)
            span.set_tag('error.msg', exception.message)
            return json(data, status=exception.status_code)
        return super().default(request, exception)

app.error_handler = CustomHandler()

def extra_type_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
    raise TypeError("%s is not JSON serializable" % repr(obj))

@app.listener('before_server_start')
async def before_srver_start(app, loop):
    queue = asyncio.Queue()
    app.queue = queue
    loop.create_task(consume(queue, app.config.ZIPKIN_SERVER))
    reporter = AioReporter(app.name, queue=queue)
    app.reporter = reporter
    tracer = BasicTracer(recorder=reporter)
    tracer.register_required_propagators()
    opentracing.tracer = tracer
    app.db = await ConnectionPool(loop=loop, reporter=reporter).init(DB_CONFIG=DB_CONFIG)

def before_request(request):
    try:
        span_context = opentracing.tracer.extract(
            format=opentracing.Format.HTTP_HEADERS,
            carrier=request.headers
        )
    except Exception as e:
        span_context = None
    handler = request.app.router.get(request)
    span = opentracing.tracer.start_span(operation_name=handler[0].__name__,
                             child_of=span_context)
    span.log_kv({'event': 'server'})
    span.set_tag('http.url', request.url)
    span.set_tag('http.method', request.method)
    ip = request.ip
    if ip:
        span.set_tag(tags.PEER_HOST_IPV4, "{}:{}".format(ip[0], ip[1]))
    return span

@app.middleware('request')
async def cros(request):
    if request.method == 'OPTIONS':
        headers = {'Access-Control-Allow-Origin': '*',
                   'Access-Control-Allow-Headers': 'Content-Type',
                   'Access-Control-Allow-Methods': 'POST, PUT, DELETE'}
        return json({'status': True}, headers=headers)
    span = before_request(request)
    request['span'] = span

@app.middleware('response')
async def cors_res(request, response):
    span = request['span'] if 'span' in request else None
    if response is None:
        return response
    result = {'status': True}
    if not isinstance(response, HTTPResponse):
        if isinstance(response, tuple) and len(response) == 2:
            result.update({
                'data': response[0],
                'pagination': response[1]
            })
        else:
            result.update({'data': response})
        response = json(result)
        if span: span.set_tag('http.status_code', "200")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, PUT, DELETE"
    if span: await request.app.reporter.finish(request.app.name, span)
    return response

@app.exception(RequestTimeout)
def timeout(request, exception):
    return json({'message': 'Request Timeout'}, 408)

@app.exception(NotFound)
def notfound(request, exception):
    return json({'message': 'Requested URL {} not found'.format(request.url)}, 404)

def create_span(span_id, parent_span_id, trace_id, span_name,
                start_time, duration, annotations,
                binary_annotations):
    span_dict = {
        'traceId': trace_id,
        'name': span_name,
        'id': span_id,
        'parentId': parent_span_id,
        'timestamp': start_time,
        'duration': duration,
        'annotations': annotations,
        'binaryAnnotations': binary_annotations
    }
    return span_dict

async def consume(q, zs):
    async with aiohttp.ClientSession() as session:
        while True:
            # wait for an item from the producer
            try:
                span = await q.get()
                annotations = []
                binary_annotations = []
                annotation_filter = set()
                service_name = span.tags.pop('component') if 'component' in span.tags else None
                endpoint = {'serviceName': service_name if service_name else 'service'}
                if span.tags:
                    for k, v in span.tags.items():
                        binary_annotations.append({
                            'endpoint': endpoint,
                            'key': k,
                            'value': v
                        })
                for log in span.logs:
                    event = log.key_values.get('event') or ''
                    payload = log.key_values.get('payload')
                    an = []
                    start_time = int(span.start_time*1000000)
                    duration = int(span.duration*1000000)
                    if event == 'client':
                        an = {'cs': start_time,
                            'cr': start_time + duration}
                    elif event == 'server':
                        an = {'sr': start_time,
                            'ss': start_time + duration}
                    else:
                        binary_annotations["%s@%s" % (event, str(log.timestamp))] = payload
                    for k, v in an.items():
                        annotations.append({
                            'endpoint': endpoint,
                            'timestamp': v,
                            'value': k
                        })
                span_record = create_span(
                    utils.id_to_hex(span.context.span_id),
                    utils.id_to_hex(span.parent_id),
                    utils.id_to_hex(span.context.trace_id),
                    span.operation_name,
                    start_time,
                    duration,
                    annotations,
                    binary_annotations,
                )
                async with session.post(zs, json=[span_record]) as res:
                    logger.info(await res.text())
            except Exception as e:
                logger.error("dddddddddd {}".format(e))
                raise e
            finally:
                q.task_done()
