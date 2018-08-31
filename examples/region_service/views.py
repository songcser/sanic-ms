import logging
import ujson

from sanic import Blueprint

from sanicms import doc
from models import Province, City

region_bp = Blueprint('region', url_prefix='regions')


@region_bp.post('/cities', name='add_city')
@doc.summary('add city')
@doc.description('add city')
@doc.consumes(City)
@doc.produces({'id': id})
async def add_city(request):
    data = request['data']
    async with request.app.db.transaction(request) as cur:
        record = await cur.fetchrow(
            """ INSERT INTO cities(name)
                VALUES($1)
                RETURNING id
            """, data['name']
        )
        return {'id': record['id'])
    

@region_bp.get('/cities/<id:int>', name='get_city')
@doc.summary('get city info')
@doc.produces(City)
async def get_city(request, id):
    async with request.app.db.acquire(request) as cur:
        records = await cur.fetch(
            ''' SELECT * FROM cities WHERE id = $1 ''', id
        )
        return records
