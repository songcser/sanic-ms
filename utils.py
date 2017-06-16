#!/usr/bin/env python
# -*- coding: utf-8 -*-

def jsonify(records):
    """
    Parse asyncpg record response into JSON format
    """
    return [dict(r.items()) for r in records]

def insert_sql(table, **kwargs):
    sql = ["INSERT INTO {} (".format(table)]
    index, names, values, params = 1, [], [], []
    for k, v in kwargs.items():
        values.append("${}".format(index))
        if isinstance(v, list):
            names.append(k)
            params.append('array{}'.format(v))
        elif isinstance(v, dict):
            id = getattr(v, "id", None)
            if id:
                names.append(k)
                params.append(id)
        else:
            names.append(k)
            params.append(v)
    sql.append(",".join(names)).append("VALUES (").append(",".join(values)).append(");").append("RETURNING id")
    return " ".join(sql), params

def select_sql(sql=None, limit=None, offset=None, **kwargs):
    index, params, sub = 1, [], []
    for k, v in kwargs.items():
        if not v: continue
        sub.append("%s = $%s" % (k, index))
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
