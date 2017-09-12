import logging
import ujson
import time
import asyncio

from sanic import Blueprint

from sanic_ms import doc
from sanic_ms.utils import *
from sanic_ms.exception import ServerError
from models import *

logger = logging.getLogger('sanic')

user_bp = Blueprint('user', url_prefix='users')


async def async_request(datas):
    results = await asyncio.gather(*[data[2] for data in datas])
    for index, obj in enumerate(results):
        data = datas[index]
        data[0][data[1]] = results[index]

@user_bp.get('/')
@doc.summary("获取用户列表")
@doc.produces([Users])
async def get_users_list(request):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(""" SELECT * FROM users """)
        return records

@user_bp.get('/<id:int>')
@doc.summary("获取用户信息")
@doc.produces([Users])
async def get_users_list(request, id):
    async with request.app.db.acquire(request) as cur:
        record = await cur.fetch(
            """ SELECT * FROM users WHERE id = $1 """, id)
        datas = [
            [record, '', get_articles_by_id(request, record['articles'])]
        ]
        return record
