#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from playhouse.migrate import *
from peewee import ProgrammingError
from config import DB_CONFIG
from models import *

logger = logging.getLogger('sanic')

class MigrationModel(object):
    _db = None
    _migrator = None

    def __init__(self):
        if self._model:
            dis = getattr(self._model._meta, 'distribute', None)
            if dis:
                qc = self._db.compiler()
                qt = list(qc.create_table(self._model, safe=True))
                qt[0] += dis
                self._db.execute_sql(*tuple(qt))
            else:
                self._db.create_table(self._model, safe=True)
            self._name = self._model._meta.db_table

    def add_column(self, col, field=None):
        print('Migrating==> [%s] add_column: %s' % (self._name, col))
        field = getattr(self._model, col) if not field else field
        return self.migrator.add_column(self._name, col, field)

    def rename_column(self, old, new):
        print('Migrating==> [%s] rename_column: (%s)-->(%s)' % (self._name, old, new))
        return self.migrator.rename_column(self._name, old, new)

    def drop_column(self, col):
        print('Migrating==> [%s] drop_column: %s' % (self._name, col))
        return self.migrator.drop_column(self._name, col)

    def drop_not_null(self, col):
        print('Migrating==> [%s] drop_not_null: %s' % (self._name, col))
        return self.migrator.drop_not_null(self._name, col)

    def add_not_null(self, col):
        print('Migrating==> [%s] add_not_null: %s' % (self._name, col))
        return self.migrator.add_not_null(self._name, col)

    def rename_table(self, name):
        print('Migrating==> [%s] rename_table: %s' % (self._name, name))
        return self.migrator.rename_table(self._name, name)

    def add_index(self, cols, unique=False):
        print('Migrating==> [%s] add_index: %s' % (self._name, cols))
        return self.migrator.add_index(self._name, cols, unique)

    def drop_index(self, col):
        print('Migrating==> [%s] drop_index: %s' % (self._name, col))
        return self.migrator.drop_index(self._name, col)
