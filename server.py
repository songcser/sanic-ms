#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from sanic import Sanic
from sanic.response import json, text

from views import data_bl
from db import BaseConnection
from client import Client

logger = logging.getLogger('sanic')
app = Sanic(__name__)

@app.listener('before_server_start')
async def before_srver_start(app, loop):
    app.db = await BaseConnection(loop=loop).init()
    app.client =  Client(loop=loop)

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    app.client.close()

@app.middleware('request')
async def cros(request):
    logger.info(request.method)
    if request.method == 'OPTIONS':
        headers = {'Access-Control-Allow-Origin': '*'}
        return response.json({'message': 'Hello World'}, headers=headers)

@app.middleware('response')
async def cors_res(request, response):
    response.headers["Access-Control-Allow-Origin"] = "*"

@app.route("/")
async def test(request):
    return text('Hello world!')

@app.route("/<test:int>/<ffff>")
async def test_dddd(request):
    return text('Hello world!')

app.blueprint(data_bl)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
