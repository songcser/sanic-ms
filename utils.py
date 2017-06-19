#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

def jsonify(records):
    """
    Parse asyncpg record response into JSON format
    """
    return [dict(r.items()) for r in records]

def insert_sql(table, data):
    sql = ["INSERT INTO {} (".format(table)]
    index, names, values, params = 1, [], [], []
    if 'create_time' not in data:
        data.update({'create_time': datetime.datetime.utcnow()})
    for k, v in data.items():
        if k == "id":
            continue
        if isinstance(v, list):
            names.append(k)
            for value in v:
                ids = []
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

def select_sql(table, values=None, limit=None, offset=None, **kwargs):
    sql = [""" SELECT {} FROM {}""".format(",".join(values) if values else "*", table)]
    index, params, sub = 1, [], []
    for k, v in kwargs.items():
        if not v: continue
        sub.append("{} = ${}".format(k, index))
        params.append(v)
        index += 1
    if sub:
        sql.append("WHERE")
        sql.append(" AND ".join(sub))
    if limit:
        sql.append("LIMIT ${}".format(index))
        params.append(limit)
        index += 1
    if offset:
        sql.append("OFFSET ${}".format(index))
        params.append(offset)
        index
    return " ".join(sql), params

def update_sql(table, t_id, **kwargs):
    index, up, sub, where, args =1, "UPDATE {} SET".format(table), [], "WHERE id={}".format(t_id), []
    for k, v in kwargs.items():
        if not v or k =='id': continue
        sub.append("{} = ${}".format(k, index))
        args.append(v)
        index += 1
    sets = ",".join(sub)
    return " ".join([up, sets, where]), args
