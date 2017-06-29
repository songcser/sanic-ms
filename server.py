#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime

from sanic import Sanic
from sanic.handlers import ErrorHandler
from sanic.response import json, text, HTTPResponse
from sanic_openapi import swagger_blueprint, openapi_blueprint
from asyncpg import Record

from config import DB_CONFIG
from ethicall_common.db import ConnectionPool
from ethicall_common.client import Client
from ethicall_common.utils import jsonify
from ethicall_common.exception import CustomException

logger = logging.getLogger('sanic')
# make app
app = Sanic(__name__)

app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)

class CustomHandler(ErrorHandler):

    def default(self, request, exception):
        if isinstance(exception, CustomException):
            data = {
                'message': exception.message,
                'code': exception.code,
            }
            if exception.error:
                data.update({'error': exception.error})
            return json(data, status=exception.status_code)
        return super().default(request, exception)

app.error_handler = CustomHandler()

def extra_type_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
    raise TypeError("%s is not JSON serializable" % repr(obj))

@app.listener('before_server_start')
async def before_srver_start(app, loop):
    app.db = await ConnectionPool(loop=loop).init(DB_CONFIG=DB_CONFIG)


@app.middleware('request')
async def cros(request):
    if request.method == 'OPTIONS':
        headers = {'Access-Control-Allow-Origin': '*',
                   'Access-Control-Allow-Headers': 'Content-Type',
                   'Access-Control-Allow-Methods': 'POST, PUT, DELETE'}
        return json({'status': True}, headers=headers)

@app.middleware('response')
async def cors_res(request, response):
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
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, PUT, DELETE"
    return response
