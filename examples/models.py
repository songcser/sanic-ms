import datetime
from peewee import *
from playhouse.postgres_ext import *
from sanic_ms import doc

class Users(Model):
    id = PrimaryKeyField()
    create_time = DateTimeField(verbose_name='创建时间', default=datetime.datetime.utcnow)
    name = CharField(max_length=128, verbose_name='名称')
    age = IntegerField(null=False, verbose_name='年龄')
    sex = CharField(max_length=32, verbose_name='性别')

    class Meta:
        db_table = 'users'
