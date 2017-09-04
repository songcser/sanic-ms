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

@user_bp.get('/')
@doc.summary("获取用户信息")
@doc.produces([Users])
async def get_users_list(request):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(""" SELECT * FROM users """)
        return records
