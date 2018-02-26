import datetime

from peewee import Model, DateTimeField, IntegerField, PrimaryKeyField, \
    CharField
from sanicms import doc


class ProvinceApi:
    id = int
    name = doc.String('name')


class CityApi:
    id = int
    name = doc.String("name")
    province_id = ProvinceApi


class RoleApi:
    id = int
    name = doc.String('name')


class Users(Model):
    id = PrimaryKeyField()
    create_time = DateTimeField(verbose_name='create time',
                                default=datetime.datetime.utcnow)
    name = CharField(max_length=128, verbose_name="user's name")
    age = IntegerField(null=False, verbose_name="user's age")
    # sex = CharField(max_length=32, verbose_name="user's sex")
    city_id = IntegerField(verbose_name='city for user', help_text=CityApi)
    role_id = IntegerField(verbose_name='role for user', help_text=RoleApi)

    class Meta:
        table_name = 'users'
