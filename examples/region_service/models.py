import datetime

from peewee import (
    Model,
    DateTimeField,
    IntegerField,
    PrimaryKeyField,
    CharField,
)


class Province(Model):
    
    id = PrimaryKeyField()
    name = CharField(max_length=32, verbose_name='provice name')
    create_time = DateTimeField(verbose_name='create time',
                                default=datetime.datetime.utcnow)

    class Meta:
        table_name = 'provinces'

class City(Model):

    id = PrimaryKeyField()
    name = CharField(max_length=32, verbose_name='city name')
    province_id = IntegerField(null=False, verbose_name='province id')
    create_time = DateTimeField(verbose_name='create time',
                                default=datetime.datetime.utcnow)

    class Meta:
        table_name = 'cities'
