import logging
import ujson

from sanic import Blueprint

from sanicms import doc
from models import Role

role_bp = Blueprint('region', url_prefix='regions')


@role_bp.post('/roles', name='add_role')
@doc.summary('add role')
@doc.description('add role')
@doc.consumes(Role)
@doc.produces({'id': id})
async def add_role(request):
    data = request['data']
    async with request.app.db.transaction(request) as cur:
        record = await cur.fetchrow(
            """ INSERT INTO roles(name)
                VALUES($1)
                RETURNING id
            """, data['name']
        )
        return {'id': record['id']}
    

@role_bp.get('/roles/<id:int>', name='get_role')
@doc.summary('get city info')
@doc.produces(Role)
async def get_city(request, id):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(
            ''' SELECT * FROM roles WHERE id = $1 ''', id
        )
        return records
