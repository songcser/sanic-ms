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

@logger()
async def get_city_by_id(request, id):
    cli = request.app.client.cli(request)
    async with cli.get('/cities/{}'.format(id)) as res:
        return await res.json()

@logger()
async def get_role_by_id(request, id):
    cli = request.app.client.cli(request)
    async with cli.get('/roles/{}'.format(id)) as res:
        return await res.json()

async def async_request(datas):
    # async handler request
    results = await asyncio.gather(*[data[2] for data in datas])
    for index, obj in enumerate(results):
        data = datas[index]
        data[0][data[1]] = results[index]

@user_bp.get('/')
@doc.summary("get user list")
@doc.produces([Users])
async def get_users_list(request):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(""" SELECT * FROM users """)
        return records

@user_bp.get('/<id:int>')
@doc.summary("get user info")
@doc.produces(Users)
async def get_users_list(request, id):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(
            """ SELECT * FROM users WHERE id = $1 """, id)
        datas = [
            [records, 'city_id', get_city_by_id(request, records['city_id'])]
            [records, 'role_id', get_role_by_id(request, records['role_id'])]
        ]
        return records
