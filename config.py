# -*- coding: utf-8 -*-
'''
Create on 2017-04-24
@author: zhaoye
'''

import os

APP_NAME = 'visit-service'

DB_CONFIG = {
    'host':  os.environ.get('POSTGRES_SERVICE_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_SERVICE_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_SERVICE_PASSWORD', None),
    'port': os.environ.get('POSTGRES_SERVICE_PORT', 5432),
    'database': os.environ.get('POSTGRES_SERVICE_DB_NAME', 'postgres')
}

REDIS_DB_CONFIG = {
    'host': os.environ.get('redis_host', 'redis'),
    'port': os.environ.get('redis_port', 6379),
}

DEBUG = True
WORKERS = 2
ODOO_MS = "http://{}:{}/ms_odoo".format(
    os.environ.get('MS_ODOO_SERVICE_HOST', '192.168.2.81'),
    os.environ.get('MS_ODOO_SERVICE_PORT', '8002'))
ODOO_URL = os.environ.get('odoo_url', 'http://192.168.2.81:48469')

ENV_NAME = None

ZIPKIN_SERVER = 'http://192.168.2.20:9411/api/v1/spans'
