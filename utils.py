#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import arrow

logger = logging.getLogger('sanic')

def jsonify(records):
    """
    Parse asyncpg record response into JSON format
    """
    return [dict(r.items()) for r in records]

def insert_sql(table, data):
    sql = ["INSERT INTO {} (".format(table)]
    index, names, values, params = 1, [], [], []
    now = arrow.utcnow()
    if 'create_time' not in data:
        data.update({'create_time': now.naive})
    else:
        data.update({'create_time': now.naive})
    for k, v in data.items():
        if k == "id" or v is None:
            continue
        if isinstance(v, list):
            names.append(k)
            ids = []
            for value in v:
                if isinstance(value, dict) and 'id' in value:
                    ids.append(value['id'])
                else:
                    ids.append(value)
            #params.append('{ %s }' % ",".join('"%s"' % i for i in ids))
            params.append(ids)
            values.append("${}".format(index))
            index += 1
        elif isinstance(v, dict):
            id = v["id"] if "id" in v else None
            if id:
                names.append(k)
                params.append(id)
                values.append("${}".format(index))
                index += 1
        else:
            names.append(k)
            params.append(v)
            values.append("${}".format(index))
            index += 1
    sql.append('{}) VALUES ({}) RETURNING id'.format(",".join(names), ",".join(values)))
    return " ".join(sql), params

def select_sql(table, values=None, limit=None, offset=None, order_by=None, **kwargs):
    sql = [""" SELECT {} FROM {}""".format(",".join(values) if values else "*", table)]
    index, params, sub = 1, [], []
    for k, v in kwargs.items():
        if v is None: continue
        if v == 'NULL':
            sub.append("{} is NULL".format(k))
        elif isinstance(v, list):
            logger.info(v)
            sub.append("{} in ({})".format(k, ",".join(v)))
        else:
            sub.append("{} = ${}".format(k, index))
            params.append(v)
            index += 1
    if sub:
        sql.append("WHERE")
        sql.append(" AND ".join(sub))
    if order_by:
        sql.append("ORDER BY {}".format(order_by))
    if limit:
        sql.append("LIMIT ${}".format(index))
        params.append(limit)
        index += 1
    if offset is not None:
        sql.append("OFFSET ${}".format(index))
        params.append(offset)
        index += 1
    return " ".join(sql), params

def update_sql(table, t_id, **kwargs):
    index, up, sub, where, params =1, "UPDATE {} SET".format(table), [], "WHERE id={}".format(t_id), []
    for k, v in kwargs.items():
        if not v or k =='id' or k == 'create_time': continue
        if isinstance(v, list):
            ids = []
            for value in v:
                if isinstance(value, dict) and 'id' in value:
                    ids.append(value['id'])
                else:
                    ids.append(value)
            params.append(ids)
            sub.append("{} = ${}".format(k, index))
            index += 1
        elif isinstance(v, dict):
            id = v['id'] if 'id' in v else None
            if id:
                params.append(id)
                sub.append("{} = ${}".format(k, index))
                index += 1
        else:
            params.append(v)
            sub.append("{} = ${}".format(k, index))
            index += 1
    sets = ",".join(sub)
    return " ".join([up, sets, where]), params
