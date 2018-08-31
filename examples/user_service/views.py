import logging
import ujson
import time
import asyncio

from sanic import Blueprint

from sanicms import doc
from sanicms.utils import *
from sanicms.exception import ServerError
from sanicms.loggers import logger
from models import *

_logger = logging.getLogger('sanic')

user_bp = Blueprint('user', url_prefix='users')

@logger()
async def get_city_by_id(request, id):
    cli = request.app.region_client.cli(request)
    async with cli.get('/cities/{}'.format(id)) as res:
        return await res.json()

@logger()
async def get_role_by_id(request, id):
    cli = request.app.client.cli(request)
    async with cli.get('/roles/{}'.format(id)) as res:
        return await res.json()


@user_bp.post('/', name="create_user")
@doc.summary('create user')
@doc.description('create user info')
@doc.consumes(User)
@doc.produces({'id': int})
async def create_user(request):
    data = request['data']
    async with request.app.db.transaction(request) as cur:
        record = await cur.fetchrow(
            """ INSERT INTO users(name, age, city_id, role_id)
                VALUES($1, $2, $3, $4, $5)
                RETURNING id
            """, data['name'], data['age'], data['city_id'], data['role_id']
        )
        return {'id': record['id']}

@user_bp.get('/', name="get_users")
@doc.summary("get user list")
@doc.produces([User])
async def get_users(request):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(""" SELECT * FROM users """)
        return records

@user_bp.get('/<id:int>', name="get_user")
@doc.summary("get user info")
@doc.produces(User)
async def get_user(request, id):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(
            """ SELECT * FROM users WHERE id = $1 """, id)
        datas = [
            [records, 'city_id', get_city_by_id(request, records['city_id'])],
            [records, 'role_id', get_role_by_id(request, records['role_id'])]
        ]
        await async_request(datas)
        return records
