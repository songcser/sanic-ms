#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from sanic import Sanic
from sanic.response import json, text
from sanic_openapi import swagger_blueprint, openapi_blueprint

from config import DB_CONFIG
from ethicall_common.db import BaseConnection
from ethicall_common.client import Client

logger = logging.getLogger('sanic')
# make app
app = Sanic(__name__)

app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)


@app.listener('before_server_start')
async def before_srver_start(app, loop):
    app.db = await BaseConnection(loop=loop).init(DB_CONFIG=DB_CONFIG)
    app.client =  Client(loop=loop)

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    app.client.close()

@app.middleware('request')
async def cros(request):
    if request.method == 'OPTIONS':
        headers = {'Access-Control-Allow-Origin': '*',
                   'Access-Control-Allow-Headers': 'Content-Type',
                   'Access-Control-Allow-Method': 'POST, PUT, DELETE'}
        return json({'message': 'Hello World'}, headers=headers)

@app.middleware('response')
async def cors_res(request, response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Method"] = "POST, PUT, DELETE"

