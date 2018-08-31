#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime

from playhouse.migrate import *
from peewee import ProgrammingError

from sanicms import load_config

config = load_config()

db_manager = PostgresqlDatabase(**config['DB_CONFIG'])
migrator = PostgresqlMigrator(db_manager)

logger = logging.getLogger('sanic')

class MigrationRecord(Model):
    id = PrimaryKeyField()
    table = CharField()
    version = CharField()
    author = CharField()
    create_time = DateTimeField(verbose_name='创建时间',
                                default=datetime.datetime.utcnow())

    class Meta:
        table_name = 'migration_record'
        database = db_manager

def info(version=None, author=None, datetime=None):
    def decorator(fn):
        @functools.wraps(fn)
        def _decorator(*args, **kwargs):
            if not version: return None
            table = args[0]._model._meta.db_table
            mr = MigrationRecord.select().where(
                MigrationRecord.version == version,
                MigrationRecord.table == table
            )
            if mr: return None
            MigrationRecord.create(
                table=table, version=version, author=author if author else '',
                datetime=datetime if datetime else datetime.utcnow())
            fn(*args, **kwargs)
        _decorator.version = version
        _decorator.author = author
        _decorator.datetime = datetime
        return _decorator
    decorator.version = version
    decorator.author = author
    decorator.datetime = datetime
    return decorator

class MigrationModel:
    _db = db_manager
    _migrator = migrator
    _model = None

    def __init__(self):
        self._mr = MigrationRecord()
        #  self._mr.create_table(safe)
        self._db.create_tables([self._mr], safe=True)
        if self._model:
            self._model._meta.database = self._db
            self._model.create_table(safe=True)
            self._name = self._model._meta.table_name

    def add_column(self, col, field=None):
        print('Migrating==> [%s] add_column: %s' % (self._name, col))
        field = getattr(self._model, col) if not field else field
        return self._migrator.add_column(self._name, col, field)

    def rename_column(self, old, new):
        print('Migrating==> [%s] rename_column: (%s)-->(%s)' % (self._name, old, new))
        return self._migrator.rename_column(self._name, old, new)

    def drop_column(self, col):
        print('Migrating==> [%s] drop_column: %s' % (self._name, col))
        return self._migrator.drop_column(self._name, col)

    def drop_not_null(self, col):
        print('Migrating==> [%s] drop_not_null: %s' % (self._name, col))
        return self._migrator.drop_not_null(self._name, col)

    def add_not_null(self, col):
        print('Migrating==> [%s] add_not_null: %s' % (self._name, col))
        return self._migrator.add_not_null(self._name, col)

    def rename_table(self, name):
        print('Migrating==> [%s] rename_table: %s' % (self._name, name))
        return self._migrator.rename_table(self._name, name)

    def add_index(self, cols, unique=False):
        print('Migrating==> [%s] add_index: %s' % (self._name, cols))
        return self._migrator.add_index(self._name, cols, unique)

    def drop_index(self, col):
        print('Migrating==> [%s] drop_index: %s' % (self._name, col))
        return self._migrator.drop_index(self._name, col)

    def auto_migrate(self):
        for fn in dir(self):
            if fn.startswith('migrate_') and hasattr(getattr(self, fn), '__call__'):
                getattr(self, fn)()
