import datetime

from peewee import (
    Model,
    DateTimeField,
    IntegerField,
    PrimaryKeyField,
    CharField,
)


class Role(Model):

    id = PrimaryKeyField()
    name = CharField(max_length=128, verbose_name='role name')

